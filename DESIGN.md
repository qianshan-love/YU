# 县志智能编纂Agent系统架构设计文档

## 项目概述

本项目实现一个全流程自动化的县志智能编纂系统，核心目标是通过Agent协同实现"用户零操作、无学习压力"的智能编纂。系统采用分层架构，由**调度中枢Agent**统一协调多个**功能执行Agent**，实现从需求问询到归档保存的完整闭环。

---

## 一、整体架构设计

### 1.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          县志智能编纂Agent系统                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        接入层 (API Gateway)                           │   │
│  │  RESTful API + WebSocket                                             │   │
│  │  - 需求接收接口                                                       │   │
│  │  - 资料上传接口                                                       │   │
│  │  - 成果查询接口                                                       │   │
│  │  - 进度监控接口                                                       │   │
│  │  - 版本管理接口                                                       │   │
│  │  - 审核操作接口                                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     调度中枢 Agent (Dispatcher)                       │   │
│  │  【设计模式：Plan and Execute】                                        │   │
│  │                                                                         │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐│   │
│  │  │  规划模块    │  │  执行模块    │  │  监控模块    │  │ 状态管理  ││   │
│  │  │  Planner     │  │  Executor    │  │  Monitor     │  │  Manager  ││   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘│   │
│  │         │                │                │                │          │   │
│  │         └────────────────┼────────────────┼────────────────┘          │   │
│  │                          │                │                            │   │
│  │                      ┌───▼────────────────▼───┐                         │   │
│  │                      │   LangGraph 状态机      │                         │   │
│  │                      └────────────────────────┘                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                 ┌──────────────────┼──────────────────┐                    │
│                 ▼                  ▼                  ▼                    │
│  ┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐ │
│  │ 任务规划 Agent      │ │ 撰稿生成 Agent      │ │ 审校校验 Agent      │ │
│  │ TaskPlanner Agent   │ │ Drafting Agent      │ │ ReviewAgent         │ │
│  │ 【设计模式：ReAct】 │ │ 【设计模式：ReAct】 │ │ 【设计模式：ReAct】 │ │
│  └─────────────────────┘ └─────────────────────┘ └─────────────────────┘ │
│          │                     │                      │                    │
│          ▼                     ▼                      ▼                    │
│  ┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐ │
│  │ 知识规范 Agent      │ │ 版本控制 Agent      │ │ 成员管理 Agent      │ │
│  │ Knowledge Agent     │ │ VersionAgent        │ │ MemberAgent         │ │
│  │ 【设计模式：ReAct】 │ │ 【设计模式：ReAct】 │ │ 【设计模式：ReAct】 │ │
│  └─────────────────────┘ └─────────────────────┘ └─────────────────────┘ │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                              工具链层 (Tools)                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │资料检索  │ │文档解析  │ │规范校验  │ │版本管理  │ │用户交互  │          │
│  │   Tool   │ │   Tool   │ │   Tool   │ │   Tool   │ │   Tool   │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
├─────────────────────────────────────────────────────────────────────────────┤
│                              数据层 (Data)                                   │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐         │
│  │  MySQL │ │ MongoDB│ │  Redis │ │   ES   │ │ Neo4j  │ │  File  │         │
│  │(结构化)│ │(非结构化)│ │ (缓存)  │ │(检索)   │ │(知识图谱)│ │(存储)  │         │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 二、调度中枢 Agent 架构设计

### 2.1 设计模式选择：Plan and Execute

**选择理由**：

| 对比维度 | Plan and Execute | ReAct |
|---------|-----------------|-------|
| **适用场景** | 复杂多步骤任务，需要全局规划 | 简单决策-执行循环 |
| **优势** | 提前规划，避免盲目探索；支持并行执行 | 响应快速，灵活调整 |
| **劣势** | 规划阶段耗时；初始规划可能不完善 | 可能陷入循环；缺乏全局视角 |
| **调度场景** | ✅ 需要管理8个阶段、多个Agent协调 | ❌ 复杂度不足 |

**调度中枢核心职责**：
1. **全局规划**：分析用户需求，生成完整的编纂计划（目录、任务分配、里程碑）
2. **分步执行**：按计划调度功能Agent，监控执行进度
3. **动态调整**：根据执行结果（如审核驳回、成员变动）调整后续计划
4. **状态维护**：统一管理整个编纂流程的全局状态

### 2.2 调度中枢核心模块

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         调度中枢 Agent                                   │
│                      (Dispatcher Agent)                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │  1. Planner（规划模块）                                            │ │
│  │     ┌─────────────────────────────────────────────────────────┐   │ │
│  │     │ 需求分析 → 目录生成 → 任务分配 → 版本规划 → 审核规划     │   │ │
│  │     └─────────────────────────────────────────────────────────┘   │ │
│  │                                                                     │ │
│  │     输入：用户需求、写志组成员信息                                  │ │
│  │     输出：编纂计划（CompilationPlan）                               │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                              │                                           │
│                              ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │  2. Executor（执行模块）                                            │ │
│  │     ┌─────────────────────────────────────────────────────────┐   │ │
│  │     │                                                       │   │ │
│  │     │  按照计划调度功能Agent，处理执行结果                     │   │ │
│  │     │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │   │ │
│  │     │  │需求问询 │  │章节起草 │  │章节审核 │  │终稿确认 │  │   │ │
│  │     │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  │   │ │
│  │     └─────────────────────────────────────────────────────────┘   │ │
│  │                                                                     │ │
│  │     输入：编纂计划、当前状态、功能Agent执行结果                      │ │
│  │     输出：执行指令、状态更新                                        │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                              │                                           │
│                              ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │  3. Monitor（监控模块）                                            │ │
│  │     ┌─────────────────────────────────────────────────────────┐   │ │
│  │     │ - 进度跟踪：监控各阶段完成度                             │   │ │
│  │     │ - 异常检测：资料缺失、审核驳回、模型异常                 │   │ │
│  │     │ - 事件监听：成员变动、用户交互                            │   │ │
│  │     │ - 超时监控：审核超时、任务超时                            │   │ │
│  │     └─────────────────────────────────────────────────────────┘   │ │
│  │                                                                     │ │
│  │     输入：执行日志、状态变化                                        │ │
│  │     输出：告警、恢复策略                                            │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                              │                                           │
│                              ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │  4. State Manager（状态管理模块）                                  │ │
│  │     ┌─────────────────────────────────────────────────────────┐   │ │
│  │     │ - 全局状态：任务信息、阶段、成员、章节状态                │   │ │
│  │     │ - 上下文记忆：对话历史、执行记录、版本信息                │   │ │
│  │     │ - 持久化：Redis缓存 + MongoDB长存储                       │   │ │
│  │     └─────────────────────────────────────────────────────────┘   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.3 调度中枢状态机设计（基于LangGraph）

```python
# 编纂阶段枚举
class CompilationPhase(Enum):
    REQUIREMENT_INQUIRY = "requirement_inquiry"      # 阶段1：需求问询
    CATALOG_GENERATION = "catalog_generation"        # 阶段2：目录生成
    TASK_ASSIGNMENT = "task_assignment"              # 阶段3：任务分配
    CHAPTER_DRAFTING = "chapter_drafting"            # 阶段4：章节起草
    CHAPTER_REVIEW = "chapter_review"                # 阶段5：章节审核
    DRAFT_REVISION = "draft_revision"                # 阶段6：稿件修改
    FINAL_REVIEW = "final_review"                    # 阶段7：终稿审核
    FINAL_CONFIRMATION = "final_confirmation"        # 阶段8：最终确认
    ARCHIVING = "archiving"                          # 阶段9：归档保存
    COMPLETED = "completed"                          # 阶段10：完成
    ERROR = "error"                                  # 异常处理

# LangGraph状态定义
@dataclass
class DispatcherState:
    """调度中枢全局状态"""
    # ============ 基础信息 ============
    task_id: str                                      # 任务唯一ID
    user_id: str                                      # 用户ID
    created_at: datetime                              # 创建时间
    updated_at: datetime                              # 更新时间

    # ============ 阶段与流程 ============
    current_phase: CompilationPhase                  # 当前阶段
    previous_phase: Optional[CompilationPhase]        # 上一阶段
    phase_history: List[CompilationPhase]            # 阶段历史记录

    # ============ 用户需求 ============
    user_requirements: Dict[str, Any]                # 用户原始需求
    county_info: Dict[str, Any]                      # 县志背景信息
    compilation_purpose: str                          # 编纂目的
    time_range: Tuple[datetime, datetime]            # 时间范围

    # ============ 目录结构 ============
    catalog: List[ChapterInfo]                        # 县志目录结构
    total_chapters: int                              # 总章节数

    # ============ 成员管理 ============
    members: List[MemberInfo]                        # 写志组成员
    member_changes: List[MemberChangeEvent]          # 成员变动记录

    # ============ 任务分配 ============
    task_assignments: Dict[str, TaskAssignment]       # 任务分配映射
    # 格式: {chapter_id: TaskAssignment}

    # ============ 章节状态 ============
    chapters: Dict[str, ChapterState]                # 章节状态字典
    # 格式: {chapter_id: ChapterState}

    # ============ 版本管理 ============
    versions: Dict[str, List[VersionInfo]]           # 版本信息
    # 格式: {chapter_id: [VersionInfo]}

    # ============ 审核记录 ============
    review_records: List[ReviewRecord]                # 审核记录列表

    # ============ 上下文记忆 ============
    context_memory: List[ContextMessage]             # 上下文记忆
    execution_logs: List[ExecutionLog]              # 执行日志

    # ============ 异常与状态 ============
    errors: List[ErrorInfo]                          # 异常记录
    retry_count: int = 0                             # 重试次数
    is_paused: bool = False                         # 是否暂停
    is_terminated: bool = False                      # 是否终止

# 状态转换路由
def route_next_phase(state: DispatcherState) -> str:
    """根据当前状态决定下一阶段"""

    current = state.current_phase

    # 正常流程路由
    if current == CompilationPhase.REQUIREMENT_INQUIRY:
        return "catalog_generation"

    elif current == CompilationPhase.CATALOG_GENERATION:
        return "task_assignment"

    elif current == CompilationPhase.TASK_ASSIGNMENT:
        return "chapter_drafting"

    elif current == CompilationPhase.CHAPTER_DRAFTING:
        # 检查是否所有章节已完成
        completed = all(
            ch.status in ["reviewed", "approved"]
            for ch in state.chapters.values()
        )
        return "final_review" if completed else "chapter_drafting"

    elif current == CompilationPhase.CHAPTER_REVIEW:
        last_review = state.review_records[-1] if state.review_records else None
        if last_review and last_review.status == "rejected":
            return "draft_revision"
        # 检查是否所有审核通过
        all_approved = all(
            r.status == "approved"
            for r in state.review_records
        )
        if all_approved:
            return "final_review"
        return "chapter_drafting"

    elif current == CompilationPhase.DRAFT_REVISION:
        return "chapter_review"

    elif current == CompilationPhase.FINAL_REVIEW:
        return "final_confirmation"

    elif current == CompilationPhase.FINAL_CONFIRMATION:
        if state.user_requirements.get("confirmed", False):
            return "archiving"
        return "draft_revision"

    elif current == CompilationPhase.ARCHIVING:
        return "completed"

    return "error"
```

### 2.4 调度中枢工作流程

```
用户发起编纂任务
        │
        ▼
┌─────────────────────────────┐
│ 1. Planner 规划阶段          │
│    ├─ 需求分析              │
│    ├─ 调用 TaskPlannerAgent │
│    ├─ 生成县志目录          │
│    ├─ 分配撰稿/审核任务     │
│    └─ 生成版本规划          │
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│ 2. Executor 执行循环        │
│                             │
│   while 任务未完成:         │
│     ├─ 读取当前阶段         │
│     ├─ 路由到对应节点       │
│     ├─ 调用功能Agent        │
│     ├─ 处理执行结果         │
│     ├─ 更新状态             │
│     └─ 进入下一阶段         │
│                             │
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│ 3. Monitor 实时监控         │
│    ├─ 进度跟踪              │
│    ├─ 异常检测              │
│    ├─ 事件监听（成员变动）  │
│    └─ 超时告警              │
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│ 4. 异常处理                 │
│    ├─ 资料缺失 → 索要资料   │
│    ├─ 审核驳回 → 触发修改   │
│    ├─ 成员变动 → 重分配任务 │
│    └─ 超时 → 告警+恢复     │
└─────────────────────────────┘
        │
        ▼
    任务完成/归档
```

---

## 三、功能执行Agent架构设计

### 3.1 设计模式选择：ReAct

**ReAct模式核心**：**Reasoning（推理）+ Acting（行动）**

```
┌─────────────────────────────────────────────────────────┐
│                  ReAct Agent 工作循环                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   Thought: "我需要先分析用户的需求背景..."             │
│       │                                                 │
│       ▼                                                 │
│   Action: 调用需求分析工具                              │
│       │                                                 │
│       ▼                                                 │
│   Observation: 获取到需求分析结果                       │
│       │                                                 │
│       ▼                                                 │
│   Thought: "基于需求，我需要生成目录结构..."           │
│       │                                                 │
│       ▼                                                 │
│   Action: 调用目录生成工具                              │
│       │                                                 │
│       ▼                                                 │
│   ... 循环直到任务完成 ...                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**选择ReAct的理由**：
1. **适合单一职责**：每个功能Agent专注特定领域，任务相对单一
2. **灵活应变**：能够根据工具调用结果动态调整策略
3. **调试友好**：Thought过程可追溯，便于问题排查
4. **轻量高效**：相比Plan and Execute，无需复杂规划过程

### 3.2 功能Agent统一接口

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseAgent(ABC):
    """功能Agent基类"""

    def __init__(self, agent_config: Dict[str, Any]):
        self.agent_id = agent_config.get("agent_id")
        self.agent_name = agent_config.get("agent_name")
        self.model_config = agent_config.get("model_config", {})
        self.tools = self._initialize_tools()

    @abstractmethod
    def _initialize_tools(self) -> List[Any]:
        """初始化工具集"""
        pass

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行Agent任务"""
        pass

    @abstractmethod
    def get_agent_schema(self) -> Dict[str, Any]:
        """获取Agent的Schema定义"""
        pass

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """ReAct循环执行"""
        max_iterations = 10
        iteration = 0

        thoughts = []
        actions = []
        observations = []

        while iteration < max_iterations:
            # 1. Thought: 推理下一步行动
            thought = await self._think(
                input_data=input_data,
                history=thoughts,
                previous_actions=actions,
                previous_observations=observations
            )
            thoughts.append(thought)

            # 2. 判断是否完成任务
            if self._is_done(thought):
                break

            # 3. Action: 执行工具调用
            action = await self._act(thought, input_data)
            actions.append(action)

            # 4. Observation: 获取执行结果
            observation = await self._observe(action)
            observations.append(observation)

            iteration += 1

        # 5. 生成最终结果
        result = await self._finalize(
            thoughts=thoughts,
            actions=actions,
            observations=observations
        )

        return result

    @abstractmethod
    async def _think(self, **kwargs) -> str:
        """推理过程"""
        pass

    @abstractmethod
    async def _act(self, thought: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行行动"""
        pass

    @abstractmethod
    async def _observe(self, action: Dict[str, Any]) -> Any:
        """观察执行结果"""
        pass

    def _is_done(self, thought: str) -> bool:
        """判断是否完成"""
        return "完成" in thought or "结束" in thought or "Done" in thought

    async def _finalize(self, **kwargs) -> Dict[str, Any]:
        """生成最终结果"""
        return {
            "status": "success",
            "thoughts": kwargs["thoughts"],
            "result": kwargs["observations"][-1] if kwargs["observations"] else None
        }
```

---

## 四、各功能Agent详细设计

### 4.1 任务规划 Agent (TaskPlannerAgent)

**核心职责**：
- 需求问询：与用户交互，明确编纂背景、目的、范围
- 目录生成：基于需求生成符合国标的县志目录结构
- 任务分配：根据成员数量动态分配撰稿、审核任务

**ReAct工作流**：
```
Thought: "我需要向用户询问编纂背景和需求"
    │
    ▼
Action: 调用用户交互工具，发送问题
    │
    ▼
Observation: 获取用户回答
    │
    ▼
Thought: "基于用户需求，我需要生成县志目录"
    │
    ▼
Action: 调用目录生成工具（基于国标规范）
    │
    ▼
Observation: 获取目录结构
    │
    ▼
Thought: "需要根据成员数量分配任务"
    │
    ▼
Action: 调用任务分配工具
    │
    ▼
Observation: 获取任务分配结果
    │
    ▼
Thought: "任务分配完成，结束"
```

**工具集**：
- `UserInteractionTool`: 与用户交互
- `CatalogGenerationTool`: 生成县志目录
- `TaskAssignmentTool`: 分配撰稿/审核任务
- `MemberManagementTool`: 获取成员信息

### 4.2 知识规范 Agent (KnowledgeAgent)

**核心职责**：
- 规范查询：查询《地方志书质量规定》、县志术语、行文规范
- 知识检索：从规范库、旧志、年鉴中检索相关资料
- 资料校验：校验内容的规范性

**ReAct工作流**：
```
Thought: "需要查询县志撰写规范"
    │
    ▼
Action: 调用规范查询工具
    │
    ▼
Observation: 获取规范内容
    │
    ▼
Thought: "需要检索相关历史资料"
    │
    ▼
Action: 调用知识库检索工具
    │
    ▼
Observation: 获取检索结果
    │
    ▼
Thought: "校验内容是否符合规范"
    │
    ▼
Action: 调用规范校验工具
    │
    ▼
Observation: 获取校验结果
    │
    ▼
Thought: "完成"
```

**工具集**：
- `SpecificationQueryTool`: 查询规范库
- `KnowledgeRetrievalTool`: 知识库检索
- `WebSearchTool`: 互联网检索
- `SpecificationValidationTool`: 规范校验

### 4.3 撰稿生成 Agent (DraftingAgent)

**核心职责**：
- 章节起草：根据目录、规范、资料生成章节内容
- 资料整合：整合检索资料、用户补充资料
- 版本管理：自动生成初稿版本

**ReAct工作流**：
```
Thought: "需要了解章节的具体要求和规范"
    │
    ▼
Action: 调用规范查询工具
    │
    ▼
Observation: 获取章节规范
    │
    ▼
Thought: "需要检索相关资料"
    │
    ▼
Action: 调用知识库检索工具
    │
    ▼
Observation: 获取检索结果
    │
    ▼
Thought: "检索结果不足，需要向用户索要资料"
    │
    ▼
Action: 调用用户交互工具，索要资料
    │
    ▼
Observation: 获取用户补充资料
    │
    ▼
Thought: "基于规范和资料，生成章节初稿"
    │
    ▼
Action: 调用大模型生成工具
    │
    ▼
Observation: 获取初稿内容
    │
    ▼
Thought: "生成版本并保存"
    │
    ▼
Action: 调用版本管理工具
    │
    ▼
Observation: 版本保存成功
    │
    ▼
Thought: "完成"
```

**工具集**：
- `ModelGenerationTool`: 调用大模型生成内容
- `SpecificationQueryTool`: 查询撰写规范
- `KnowledgeRetrievalTool`: 知识库检索
- `UserInteractionTool`: 与用户交互
- `VersionManagementTool`: 版本管理
- `DocumentParserTool`: 文档解析

### 4.4 审校校验 Agent (ReviewAgent)

**核心职责**：
- 系统校验：体例、文风、数据格式自动校验
- 人工审核：推送审核任务给审核成员
- 审核反馈：处理审核通过/驳回结果
- 版本对比：对比不同版本的内容差异

**ReAct工作流**：
```
Thought: "需要对新稿件进行系统校验"
    │
    ▼
Action: 调用系统校验工具（规则引擎）
    │
    ▼
Observation: 获取校验结果
    │
    ▼
Thought: "校验通过，需要推送给审核成员"
    │
    ▼
Action: 调用审核推送工具
    │
    ▼
Observation: 推送成功
    │
    ▼
Thought: "等待审核反馈"
    │
    ▼
Action: 调用审核状态查询工具
    │
    ▼
Observation: 审核驳回
    │
    ▼
Thought: "审核驳回，需要对比版本差异"
    │
    ▼
Action: 调用版本对比工具
    │
    ▼
Observation: 获取版本差异
    │
    ▼
Thought: "需要对比知识图谱，检查事实一致性"
    │
    ▼
Action: 调用知识图谱查询工具
    │
    ▼
Observation: 获取一致性检查结果
    │
    ▼
Thought: "完成"
```

**工具集**：
- `SystemValidationTool`: 系统校验（规则引擎）
- `ReviewPushTool`: 审核任务推送
- `ReviewStatusQueryTool`: 审核状态查询
- `VersionCompareTool`: 版本对比
- `KnowledgeGraphQueryTool`: 知识图谱查询
- `FactConsistencyCheckTool`: 事实一致性检查

### 4.5 版本控制 Agent (VersionAgent)

**核心职责**：
- 版本生成：自动生成版本号、保存版本内容
- 版本查询：查询历史版本
- 版本对比：对比不同版本内容
- 版本回退：回退到指定版本
- 版本归档：归档终稿版本

**ReAct工作流**：
```
Thought: "需要为新稿件生成版本"
    │
    ▼
Action: 调用版本生成工具
    │
    ▼
Observation: 版本生成成功，版本号：ch01_v001
    │
    ▼
Thought: "需要查询该章节的历史版本"
    │
    ▼
Action: 调用版本查询工具
    │
    ▼
Observation: 获取到2个历史版本
    │
    ▼
Thought: "需要对比最新两个版本的差异"
    │
    ▼
Action: 调用版本对比工具
    │
    ▼
Observation: 获取版本差异报告
    │
    ▼
Thought: "用户需要回退到上一个版本"
    │
    ▼
Action: 调用版本回退工具
    │
    ▼
Observation: 版本回退成功
    │
    ▼
Thought: "终稿审核通过，需要归档"
    │
    ▼
Action: 调用版本归档工具
    │
    ▼
Observation: 版本归档成功
    │
    ▼
Thought: "完成"
```

**工具集**：
- `VersionGenerationTool`: 版本生成
- `VersionQueryTool`: 版本查询
- `VersionCompareTool`: 版本对比
- `VersionRollbackTool`: 版本回退
- `VersionArchiveTool`: 版本归档

### 4.6 成员管理 Agent (MemberAgent)

**核心职责**：
- 成员管理：添加、删除、更新成员信息
- 任务重分配：成员变动时重新分配任务
- 成员查询：查询成员信息、任务分配情况

**ReAct工作流**：
```
Thought: "检测到成员变动，需要更新成员列表"
    │
    ▼
Action: 调用成员更新工具
    │
    ▼
Observation: 成员更新成功
    │
    ▼
Thought: "需要重新分配受影响的任务"
    │
    ▼
Action: 调用任务重分配工具
    │
    ▼
Observation: 任务重分配成功
    │
    ▼
Thought: "需要通知受影响的成员"
    │
    ▼
Action: 调用通知发送工具
    │
    ▼
Observation: 通知发送成功
    │
    ▼
Thought: "完成"
```

**工具集**：
- `MemberUpdateTool`: 成员信息更新
- `MemberQueryTool`: 成员信息查询
- `TaskReassignmentTool`: 任务重分配
- `NotificationTool`: 通知发送

---

## 五、Agent间协作方式

### 5.1 协作关系图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Agent 协作关系图                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                          调度中枢 (Dispatcher)                          │
│                               │  ↑                                       │
│         ┌─────────┬─────┬──────┴──┴───────────┬─────────┬──────────┐   │
│         │         │     │                      │         │          │   │
│         ▼         ▼     ▼                      ▼         ▼          ▼   │
│   ┌──────────┐ ┌──────────┐              ┌──────────┐ ┌──────────┐    │
│   │TaskPlanner│ │ Knowledge│              │ Drafting │ │ Review   │    │
│   │  Agent   │ │  Agent   │              │  Agent   │ │  Agent   │    │
│   └──────────┘ └──────────┘              └──────────┘ └──────────┘    │
│         │           │  ↑                       │    ↑      │          │
│         └───────────┴──┴───────────────────────┴────┴──────┘          │
│                              │                                          │
│                              ▼                                          │
│                      ┌───────────────┐                                   │
│                      │  工具链层      │                                   │
│                      └───────────────┘                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 协作数据流

```
┌────────────────────────────────────────────────────────────────────────┐
│                     数据流转流程                                        │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  调度中枢                          功能Agent                          │
│    │                                  │                               │
│    ├─► [任务指令] ───────────────────►│                               │
│    │    {action, params, context}     │                               │
│    │                                  │                               │
│    │                          ┌───────▼────────┐                      │
│    │                          │  ReAct循环    │                      │
│    │                          │  Thought     │                      │
│    │                          │  Action      │                      │
│    │                          │  Observation │                      │
│    │                          └───────┬────────┘                      │
│    │                                  │                               │
│    │                                  ▼                               │
│    │                          ┌───────────────┐                      │
│    │                          │   工具调用     │                      │
│    │                          └───────┬───────┘                      │
│    │                                  │                               │
│    │                         ┌────────▼────────┐                       │
│    │                         │  数据库/缓存    │                       │
│    │                         │  知识库/模型    │                       │
│    │                         └────────┬────────┘                       │
│    │                                  │                               │
│    │                                  ▼                               │
│    │                          ┌───────────────┐                      │
│    │                          │  结果整合     │                      │
│    │                          └───────┬───────┘                      │
│    │                                  │                               │
│    │◄─ [执行结果] ◄───────────────────│                               │
│    │    {status, data, message}       │                               │
│    │                                  │                               │
│    │                          [更新状态]                               │
│    │                          [路由到下一阶段]                         │
│    │                                                                   │
└────────────────────────────────────────────────────────────────────────┘
```

### 5.3 协作协议

#### 5.3.1 调度中枢 → 功能Agent（任务指令）

```python
@dataclass
class AgentTask:
    """调度中枢发送给功能Agent的任务指令"""
    task_id: str                    # 任务ID
    agent_type: str                 # Agent类型
    action: str                     # 操作类型
    params: Dict[str, Any]          # 参数
    context: Dict[str, Any]         # 上下文信息
    priority: int = 1               # 优先级
    timeout: int = 300              # 超时时间(秒)

# 示例：调度调度中枢向撰稿Agent发送起草任务
task = AgentTask(
    task_id="task_001",
    agent_type="drafting",
    action="draft_chapter",
    params={
        "chapter_id": "ch01",
        "chapter_title": "概述",
        "requirements": {...}
    },
    context={
        "catalog": [...],
        "previous_chapters": [...],
        "specifications": [...]
    }
)
```

#### 5.3.2 功能Agent → 调度中枢（执行结果）

```python
@dataclass
class AgentResult:
    """功能Agent返回的执行结果"""
    task_id: str                    # 任务ID
    agent_type: str                 # Agent类型
    status: str                     # 状态: success/failure/partial
    data: Dict[str, Any]            # 结果数据
    message: str                    # 消息
    errors: List[str] = field(default_factory=list)  # 错误列表
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据

# 示例：撰稿Agent返回起草结果
result = AgentResult(
    task_id="task_001",
    agent_type="drafting",
    status="success",
    data={
        "chapter_id": "ch01",
        "draft": "章节内容...",
        "word_count": 5000,
        "version_id": "ch01_v001"
    },
    message="章节起草完成",
    metadata={
        "execution_time": 120,
        "model_calls": 3,
        "sources_used": [...]
    }
)
```

#### 5.3.3 功能Agent → 功能Agent（协作调用）

```python
@dataclass
class AgentToAgentRequest:
    """功能Agent之间的协作请求"""
    from_agent: str                 # 来源Agent
    to_agent: str                   # 目标Agent
    request_type: str               # 请求类型
    params: Dict[str, Any]          # 参数
    context: Dict[str, Any] = field(default_factory=dict)  # 上下文

# 示例：撰稿Agent向知识规范Agent请求规范查询
request = AgentToAgentRequest(
    from_agent="drafting",
    to_agent="knowledge",
    request_type="query_specification",
    params={
        "chapter_type": "概述",
        "query": "概述章节的撰写规范要求"
    },
    context={
        "chapter_id": "ch01"
    }
)
```

### 5.4 协作场景示例

#### 场景1：章节起草完整流程

```
1. 调度中枢发起起草任务
   └─► DraftingAgent: DraftChapterTask

2. DraftingAgent ReAct循环
   ├─ Thought: "需要查询章节规范"
   └─► KnowledgeAgent: QuerySpecification
       └─► 返回规范内容

   ├─ Thought: "需要检索相关资料"
   └─► KnowledgeAgent: RetrieveKnowledge
       └─► 返回检索结果

   ├─ Thought: "基于规范和资料生成初稿"
   └─► ModelGenerationTool
       └─► 返回初稿内容

   ├─ Thought: "需要生成版本"
   └─► VersionAgent: GenerateVersion
       └─► 返回版本信息

   └─ 返回起草结果

3. 调度中枢接收结果，更新状态
   └─► 状态更新: chapters["ch01"].status = "drafted"

4. 调度中枢触发审核任务
   └─► ReviewAgent: ReviewChapterTask
```

#### 场景2：审核驳回修改流程

```
1. ReviewAgent执行审核
   ├─ 系统校验
   └─► 推送给审核成员

2. 审核成员驳回
   └─► ReviewAgent: 审核结果(驳回)

3. ReviewAgent返回结果
   └─► 调度中枢: AgentResult(status="rejected", message="需要修改...")

4. 调度中枢更新状态
   └─► 状态更新: chapters["ch01"].status = "pending_revision"

5. 调度中枢触发修改任务
   └─► DraftingAgent: ReviseChapterTask

6. DraftingAgent执行修改
   ├─ 对比版本差异
   ├─ 根据修改意见修改内容
   └─► 生成新版本

7. 调度中枢重新触发审核
   └─► ReviewAgent: ReviewChapterTask
```

#### 场景3：成员变动任务重分配

```
1. MemberAgent检测到成员变动
   └─► 成员A离开团队

2. MemberAgent触发任务重分配
   └─► 重新分配成员A的任务

3. 调度中枢接收变更通知
   └─► 更新状态: task_assignments = {...}

4. 调度中枢通知受影响的Agent
   ├─► DraftingAgent: 更新撰稿任务
   └─► ReviewAgent: 更新审核任务

5. 调度中枢通知新成员
   └─► 发送任务通知
```

---

## 六、完整工作流程设计

### 6.1 总体流程图

```
┌────────────────────────────────────────────────────────────────────────┐
│                      县志编纂完整流程                                    │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  用户                      调度中枢                     功能Agent       │
│   │                           │                          │            │
│   ├─ 提交编纂需求 ───────────►│                          │            │
│   │                           │                          │            │
│   │                    ┌──────▼──────────┐              │            │
│   │                    │  Planner 规划   │              │            │
│   │                    │  ├─ 需求分析    │              │            │
│   │                    │  ├─ 目录生成    │              │            │
│   │                    │  └─ 任务分配    │              │            │
│   │                    └──────┬──────────┘              │            │
│   │                           │                          │            │
│   │◄─ 需求问询 ───────────────┤                          │            │
│   ├─ 回答需求 ───────────────►│                          │            │
│   │                           │                          │            │
│   │◄─ 确认目录 ───────────────┤                          │            │
│   ├─ 确认 ──────────────────►│                          │            │
│   │                           │                          │            │
│   │                    ┌──────▼──────────┐              │            │
│   │                    │ Executor 执行   │              │            │
│   │                    │  阶段循环:       │              │            │
│   │                    │  1. 章节起草     │◄─────────────┼────┐       │
│   │                    │  2. 章节审核     │◄─────────────┼────┼──┐    │
│   │                    │  3. 修改迭代     │◄─────────────┼────┼──┼──┐ │
│   │                    │  4. 终稿整合     │◄─────────────┼────┼──┼──┼─┼─┐│
│   │                    └──────┬──────────┘              │    │  │  │ ││
│   │                           │                          │    │  │  │ ││
│   │◄─ 索要资料 ───────────────┤                          │    │  │  │ ││
│   ├─ 提供资料 ───────────────►│                          │    │  │  │ ││
│   │                           │                          │    │  │  │ ││
│   │◄─ 审核通知 ───────────────┤                          │    │  │  │ ││
│   │                           │                          │    │  │  │ ││
│   │                    ┌──────▼──────────┐              │    │  │  │ ││
│   │                    │ Monitor 监控     │              │    │  │  │ ││
│   │                    │  ├─ 进度跟踪    │              │    │  │  │ ││
│   │                    │  ├─ 异常处理    │              │    │  │  │ ││
│   │                    │  └─ 成员变动    │              │    │  │  │ ││
│   │                    └──────┬──────────┘              │    │  │  │ ││
│   │                           │                          │    │  │  │ ││
│   │◄─ 终稿预览 ───────────────┤                          │    │  │  │ ││
│   ├─ 确认归档 ───────────────►│                          │    │  │  │ ││
│   │                           │                          │    │  │  │ ││
│   │◄─ 完成通知 ───────────────┤                          │    │  │  │ ││
│   │                           │                          │    │  │  │ ││
│   │                           ▼                          ▼    ▼  ▼  ▼ ▼ ▼│
│   │                   TaskPlanner  Knowledge  Drafting  Review Version  │
│   │                      Agent      Agent      Agent   Agent   Agent   │
│   │                                                                    │
└────────────────────────────────────────────────────────────────────────┘
```

### 6.2 详细阶段流程

#### 阶段1：需求问询

```python
async def phase_requirement_inquiry(state: DispatcherState) -> DispatcherState:
    """阶段1：需求问询"""

    # 1. 调度中枢调用TaskPlannerAgent
    task = AgentTask(
        task_id=state.task_id,
        agent_type="task_planner",
        action="inquire_requirements",
        params={"user_id": state.user_id},
        context={}
    )

    # 2. TaskPlannerAgent ReAct循环
    #    Thought: "需要向用户询问编纂目的、时间范围、县志类型"
    #    Action: 调用UserInteractionTool发送问题
    #    Observation: 获取用户回答
    #    ... (多次交互)
    #    Result: 返回用户需求

    result = await dispatcher.invoke_agent(task)

    # 3. 更新状态
    state.user_requirements = result.data
    state.current_phase = CompilationPhase.CATALOG_GENERATION

    return state
```

#### 阶段2：目录生成

```python
async def phase_catalog_generation(state: DispatcherState) -> DispatcherState:
    """阶段2：目录生成"""

    # 1. 调用TaskPlannerAgent生成目录
    task = AgentTask(
        task_id=state.task_id,
        agent_type="task_planner",
        action="generate_catalog",
        params={
            "county_info": state.user_requirements.get("county_info"),
            "time_range": state.user_requirements.get("time_range"),
            "compilation_type": state.user_requirements.get("type")
        },
        context={}
    )

    # 2. TaskPlannerAgent ReAct循环
    #    Thought: "需要查询国标目录模板"
    #    Action: 调用CatalogGenerationTool
    #    Observation: 获取目录结构
    #    Result: 返回县志目录

    result = await dispatcher.invoke_agent(task)

    # 3. 更新状态
    state.catalog = result.data.get("catalog", [])
    state.total_chapters = len(state.catalog)
    state.chapters = {
        ch["chapter_id"]: ChapterState(
            chapter_id=ch["chapter_id"],
            title=ch["title"],
            status="pending"
        )
        for ch in state.catalog
    }

    # 4. 更新阶段
    state.current_phase = CompilationPhase.TASK_ASSIGNMENT

    return state
```

#### 阶段3：任务分配

```python
async def phase_task_assignment(state: DispatcherState) -> DispatcherState:
    """阶段3：任务分配"""

    # 1. 调用TaskPlannerAgent分配任务
    task = AgentTask(
        task_id=state.task_id,
        agent_type="task_planner",
        action="assign_tasks",
        params={
            "catalog": state.catalog,
            "members": state.members
        },
        context={}
    )

    # 2. TaskPlannerAgent ReAct循环
    #    Thought: "需要根据成员数量平均分配章节"
    #    Action: 调用TaskAssignmentTool
    #    Observation: 获取任务分配结果
    #    Result: 返回任务分配方案

    result = await dispatcher.invoke_agent(task)

    # 3. 更新状态
    state.task_assignments = result.data.get("assignments", {})

    # 4. 更新章节状态中的分配信息
    for chapter_id, assignment in state.task_assignments.items():
        state.chapters[chapter_id].drafters = assignment.get("drafters", [])
        state.chapters[chapter_id].reviewers = assignment.get("reviewers", [])

    # 5. 更新阶段
    state.current_phase = CompilationPhase.CHAPTER_DRAFTING

    return state
```

#### 阶段4：章节起草（循环执行）

```python
async def phase_chapter_drafting(state: DispatcherState) -> DispatcherState:
    """阶段4：章节起草（循环执行）"""

    # 1. 获取下一个待起草的章节
    next_chapter = get_next_pending_chapter(state.chapters)

    if not next_chapter:
        # 所有章节已完成
        state.current_phase = CompilationPhase.FINAL_REVIEW
        return state

    # 2. 调用DraftingAgent起草章节
    task = AgentTask(
        task_id=state.task_id,
        agent_type="drafting",
        action="draft_chapter",
        params={
            "chapter_id": next_chapter.chapter_id,
            "chapter_title": next_chapter.title,
            "catalog": state.catalog,
            "context": {
                "previous_chapters": get_previous_chapters(state, next_chapter.chapter_id),
                "specifications": get_chapter_specifications(state, next_chapter.chapter_id)
            }
        },
        context={}
    )

    # 3. DraftingAgent ReAct循环
    #    Thought: "需要查询章节撰写规范"
    #    Action: 调用KnowledgeAgent查询规范
    #    Observation: 获取规范内容
    #
    #    Thought: "需要检索相关资料"
    #    Action: 调用KnowledgeAgent检索知识
    #    Observation: 获取检索结果
    #
    #    Thought: "资料不足，需要向用户索要"
    #    Action: 调用UserInteractionTool
    #    Observation: 获取用户补充资料
    #
    #    Thought: "基于规范和资料生成初稿"
    #    Action: 调用ModelGenerationTool
    #    Observation: 获取初稿内容
    #
    #    Thought: "需要生成版本"
    #    Action: 调用VersionAgent生成版本
    #    Observation: 版本生成成功
    #    Result: 返回初稿和版本信息

    result = await dispatcher.invoke_agent(task)

    # 4. 更新章节状态
    state.chapters[next_chapter.chapter_id].status = "drafted"
    state.chapters[next_chapter.chapter_id].current_draft = result.data.get("draft")
    state.chapters[next_chapter.chapter_id].word_count = result.data.get("word_count", 0)

    # 5. 更新版本信息
    version_info = result.data.get("version")
    if next_chapter.chapter_id not in state.versions:
        state.versions[next_chapter.chapter_id] = []
    state.versions[next_chapter.chapter_id].append(version_info)

    # 6. 更新上下文记忆
    state.context_memory.append(ContextMessage(
        role="system",
        content=f"章节{next_chapter.chapter_id}初稿已完成，字数：{result.data.get('word_count', 0)}",
        timestamp=datetime.now(),
        metadata={"chapter_id": next_chapter.chapter_id, "version_id": version_info.get("version_id")}
    ))

    # 7. 检查是否所有章节都已完成起草
    all_drafted = all(
        ch.status in ["drafted", "reviewed", "approved"]
        for ch in state.chapters.values()
    )

    if all_drafted:
        state.current_phase = CompilationPhase.FINAL_REVIEW
    else:
        # 继续下一个章节
        state.current_phase = CompilationPhase.CHAPTER_REVIEW

    return state
```

#### 阶段5：章节审核

```python
async def phase_chapter_review(state: DispatcherState) -> DispatcherState:
    """阶段5：章节审核"""

    # 1. 获取下一个待审核的章节
    next_chapter = get_next_pending_review(state.chapters)

    if not next_chapter:
        # 所有章节已审核
        state.current_phase = CompilationPhase.FINAL_REVIEW
        return state

    # 2. 调用ReviewAgent审核章节
    task = AgentTask(
        task_id=state.task_id,
        agent_type="review",
        action="review_chapter",
        params={
            "chapter_id": next_chapter.chapter_id,
            "draft": state.chapters[next_chapter.chapter_id].current_draft,
            "reviewers": state.chapters[next_chapter.chapter_id].reviewers,
            "versions": state.versions.get(next_chapter.chapter_id, [])
        },
        context={}
    )

    # 3. ReviewAgent ReAct循环
    #    Thought: "需要进行系统校验"
    #    Action: 调用SystemValidationTool
    #    Observation: 获取校验结果
    #
    #    Thought: "系统校验通过，推送给审核成员"
    #    Action: 调用ReviewPushTool
    #    Observation: 推送成功
    #
    #    Thought: "等待审核结果"
    #    Action: 调用ReviewStatusQueryTool轮询
    #    Observation: 审核完成(通过/驳回)
    #
    #    Thought: "审核驳回，需要对比版本差异"
    #    Action: 调用VersionCompareTool
    #    Observation: 获取版本差异
    #    Result: 返回审核结果

    result = await dispatcher.invoke_agent(task)

    # 4. 更新审核记录
    review_record = ReviewRecord(
        chapter_id=next_chapter.chapter_id,
        reviewer_id=result.data.get("reviewer_id"),
        status=result.data.get("status"),  # approved/rejected
        comments=result.data.get("comments", ""),
        timestamp=datetime.now()
    )
    state.review_records.append(review_record)

    # 5. 根据审核结果更新状态
    if result.data.get("status") == "approved":
        state.chapters[next_chapter.chapter_id].status = "reviewed"
        # 进入下一个章节审核或进入终稿审核
        state.current_phase = CompilationPhase.CHAPTER_DRAFTING
    else:
        state.chapters[next_chapter.chapter_id].status = "pending_revision"
        state.chapters[next_chapter.chapter_id].review_comments = result.data.get("comments", "")
        # 进入修改阶段
        state.current_phase = CompilationPhase.DRAFT_REVISION

    return state
```

#### 阶段6：稿件修改

```python
async def phase_draft_revision(state: DispatcherState) -> DispatcherState:
    """阶段6：稿件修改"""

    # 1. 获取待修改的章节
    pending_chapter = get_pending_revision_chapter(state.chapters)

    if not pending_chapter:
        # 没有待修改的章节，回到起草阶段
        state.current_phase = CompilationPhase.CHAPTER_DRAFTING
        return state

    # 2. 调用DraftingAgent修改章节
    task = AgentTask(
        task_id=state.task_id,
        agent_type="drafting",
        action="revise_chapter",
        params={
            "chapter_id": pending_chapter.chapter_id,
            "current_draft": pending_chapter.current_draft,
            "review_comments": pending_chapter.review_comments,
            "versions": state.versions.get(pending_chapter.chapter_id, [])
        },
        context={}
    )

    # 3. DraftingAgent ReAct循环
    #    Thought: "需要对比当前版本和上一个版本"
    #    Action: 调用VersionCompareTool
    #    Observation: 获取版本差异
    #
    #    Thought: "根据修改意见修改内容"
    #    Action: 调用ModelGenerationTool
    #    Observation: 获取修改后的内容
    #
    #    Thought: "需要生成新版本"
    #    Action: 调用VersionAgent生成版本
    #    Observation: 版本生成成功
    #    Result: 返回修改稿和新版本

    result = await dispatcher.invoke_agent(task)

    # 4. 更新章节状态
    state.chapters[pending_chapter.chapter_id].current_draft = result.data.get("draft")
    state.chapters[pending_chapter.chapter_id].status = "drafted"  # 重新进入审核

    # 5. 更新版本信息
    new_version = result.data.get("version")
    state.versions[pending_chapter.chapter_id].append(new_version)

    # 6. 更新上下文记忆
    state.context_memory.append(ContextMessage(
        role="system",
        content=f"章节{pending_chapter.chapter_id}已根据审核意见修改，新版本：{new_version.get('version_id')}",
        timestamp=datetime.now(),
        metadata={"chapter_id": pending_chapter.chapter_id, "version_id": new_version.get("version_id")}
    ))

    # 7. 进入重新审核
    state.current_phase = CompilationPhase.CHAPTER_REVIEW

    return state
```

#### 阶段7：终稿审核

```python
async def phase_final_review(state: DispatcherState) -> DispatcherState:
    """阶段7：终稿审核"""

    # 1. 检查是否所有章节都已通过审核
    all_approved = all(
        ch.status == "reviewed"
        for ch in state.chapters.values()
    )

    if not all_approved:
        # 还有章节未通过审核，回到起草/审核阶段
        state.current_phase = CompilationPhase.CHAPTER_DRAFTING
        return state

    # 2. 整合所有章节为终稿
    task = AgentTask(
        task_id=state.task_id,
        agent_type="drafting",
        action="integrate_final_draft",
        params={
            "chapters": state.chapters,
            "catalog": state.catalog
        },
        context={}
    )

    result = await dispatcher.invoke_agent(task)

    # 3. 更新状态
    state.final_draft = result.data.get("final_draft")
    state.current_phase = CompilationPhase.FINAL_CONFIRMATION

    return state
```

#### 阶段8：最终确认

```python
async def phase_final_confirmation(state: DispatcherState) -> DispatcherState:
    """阶段8：最终确认"""

    # 1. 推送终稿给用户确认
    # (通过接入层通知用户)

    # 2. 等待用户确认
    # (通过接入层接收用户确认)

    # 3. 用户确认
    if state.user_requirements.get("confirmed", False):
        # 确认无误，进入归档
        state.current_phase = CompilationPhase.ARCHIVING
    else:
        # 用户有修改意见
        state.current_phase = CompilationPhase.DRAFT_REVISION

    return state
```

#### 阶段9：归档保存

```python
async def phase_archiving(state: DispatcherState) -> DispatcherState:
    """阶段9：归档保存"""

    # 1. 调用VersionAgent归档版本
    task = AgentTask(
        task_id=state.task_id,
        agent_type="version",
        action="archive_final_version",
        params={
            "task_id": state.task_id,
            "final_draft": state.final_draft,
            "chapters": state.chapters,
            "versions": state.versions,
            "review_records": state.review_records
        },
        context={}
    )

    result = await dispatcher.invoke_agent(task)

    # 2. 更新状态
    state.archived = True
    state.archive_info = result.data.get("archive_info")
    state.current_phase = CompilationPhase.COMPLETED

    # 3. 完成通知
    # (通过接入层通知用户)

    return state
```

---

## 七、数据模型设计

### 7.1 核心数据结构

```python
# 章节信息
@dataclass
class ChapterInfo:
    chapter_id: str                    # 章节ID
    title: str                          # 章节标题
    level: int                          # 章节层级（1=卷，2=篇，3=章，4=节）
    parent_id: Optional[str] = None    # 父章节ID
    order: int = 0                      # 排序
    word_count: int = 0                # 预计字数

# 章节状态
@dataclass
class ChapterState:
    chapter_id: str                    # 章节ID
    title: str                          # 章节标题
    status: str                         # 状态：pending/drafted/reviewed/approved
    current_draft: Optional[str] = None # 当前稿件内容
    word_count: int = 0                 # 实际字数
    drafters: List[str] = field(default_factory=list)  # 撰稿人
    reviewers: List[str] = field(default_factory=list) # 审核人
    review_comments: Optional[str] = None  # 审核意见
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

# 成员信息
@dataclass
class MemberInfo:
    member_id: str                      # 成员ID
    name: str                           # 姓名
    role: str                           # 角色：editor/reviewer/admin
    expertise: List[str] = field(default_factory=list)  # 专业领域
    workload: int = 0                   # 当前工作负载

# 任务分配
@dataclass
class TaskAssignment:
    chapter_id: str                    # 章节ID
    drafters: List[str]                 # 撰稿人列表
    reviewers: List[str]                # 审核人列表
    priority: int = 1                   # 优先级
    deadline: Optional[datetime] = None # 截止时间

# 版本信息
@dataclass
class VersionInfo:
    version_id: str                    # 版本ID
    chapter_id: str                    # 章节ID
    version_number: int                # 版本号
    content: str                       # 版本内容
    created_by: str                     # 创建者（Agent ID）
    created_at: datetime               # 创建时间
    version_type: str                  # 版本类型：initial/revised/final
    status: str                        # 状态：active/archived
    diff: Optional[str] = None         # 与上一版本的差异

# 审核记录
@dataclass
class ReviewRecord:
    chapter_id: str                    # 章节ID
    version_id: str                    # 版本ID
    reviewer_id: str                   # 审核人ID
    status: str                        # 状态：approved/rejected
    comments: str                      # 审核意见
    timestamp: datetime                # 审核时间

# 上下文消息
@dataclass
class ContextMessage:
    role: str                          # 角色：system/user/assistant
    content: str                       # 消息内容
    timestamp: datetime                # 时间戳
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据

# 执行日志
@dataclass
class ExecutionLog:
    task_id: str                       # 任务ID
    agent_type: str                    # Agent类型
    action: str                        # 操作
    status: str                        # 状态：success/failure/pending
    message: str                       # 消息
    execution_time: float              # 执行耗时（秒）
    timestamp: datetime                # 时间戳

# 异常信息
@dataclass
class ErrorInfo:
    error_type: str                    # 错误类型
    error_message: str                 # 错误消息
    phase: str                         # 发生阶段
    agent_type: Optional[str] = None    # 关联Agent
    stack_trace: Optional[str] = None   # 堆栈信息
    timestamp: datetime = field(default_factory=datetime.now)

# 成员变动事件
@dataclass
class MemberChangeEvent:
    event_type: str                    # 事件类型：added/removed/updated
    member_id: str                     # 成员ID
    old_info: Optional[MemberInfo] = None  # 旧信息
    new_info: Optional[MemberInfo] = None  # 新信息
    affected_tasks: List[str] = field(default_factory=list)  # 受影响的任务
    timestamp: datetime = field(default_factory=datetime.now)
```

### 7.2 数据存储映射

| 数据类型 | 存储位置 | 说明 |
|---------|---------|------|
| DispatcherState | Redis (热数据) + MongoDB (冷数据) | 全局状态 |
| user_requirements | MySQL | 结构化用户需求 |
| catalog | MySQL | 目录结构 |
| members | MySQL | 成员信息 |
| task_assignments | MySQL | 任务分配 |
| chapters | MySQL | 章节状态 |
| versions | MongoDB | 版本内容 |
| review_records | MySQL | 审核记录 |
| context_memory | MongoDB | 上下文记忆 |
| execution_logs | MongoDB + ES | 执行日志 |
| errors | MongoDB | 异常记录 |

---

## 八、技术实现要点

### 8.1 LangGraph实现调度中枢

```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

class DispatcherAgent:
    """调度中枢Agent"""

    def __init__(self):
        self.graph = self._build_graph()
        self.agent_coordinator = AgentCoordinator()

    def _build_graph(self) -> CompiledGraph:
        """构建LangGraph状态机"""

        # 创建状态图
        graph = StateGraph(DispatcherState)

        # 添加节点
        graph.add_node("requirement_inquiry", self._requirement_inquiry_node)
        graph.add_node("catalog_generation", self._catalog_generation_node)
        graph.add_node("task_assignment", self._task_assignment_node)
        graph.add_node("chapter_drafting", self._chapter_drafting_node)
        graph.add_node("chapter_review", self._chapter_review_node)
        graph.add_node("draft_revision", self._draft_revision_node)
        graph.add_node("final_review", self._final_review_node)
        graph.add_node("final_confirmation", self._final_confirmation_node)
        graph.add_node("archiving", self._archiving_node)
        graph.add_node("error_handler", self._error_handler_node)

        # 设置入口
        graph.set_entry_point("requirement_inquiry")

        # 添加边（状态转换）
        graph.add_edge("requirement_inquiry", "catalog_generation")

        graph.add_conditional_edges(
            "catalog_generation",
            self._route_from_catalog,
            {
                "task_assignment": "task_assignment",
                "error": "error_handler"
            }
        )

        graph.add_edge("task_assignment", "chapter_drafting")

        graph.add_conditional_edges(
            "chapter_drafting",
            self._route_from_drafting,
            {
                "next_chapter": "chapter_drafting",
                "chapter_review": "chapter_review",
                "final_review": "final_review",
                "error": "error_handler"
            }
        )

        graph.add_conditional_edges(
            "chapter_review",
            self._route_from_review,
            {
                "next_chapter": "chapter_drafting",
                "draft_revision": "draft_revision",
                "final_review": "final_review",
                "error": "error_handler"
            }
        )

        graph.add_edge("draft_revision", "chapter_review")

        graph.add_edge("final_review", "final_confirmation")

        graph.add_conditional_edges(
            "final_confirmation",
            self._route_from_confirmation,
            {
                "archiving": "archiving",
                "draft_revision": "draft_revision"
            }
        )

        graph.add_edge("archiving", END)

        # 编译图
        return graph.compile()

    # 节点实现
    async def _requirement_inquiry_node(self, state: DispatcherState) -> DispatcherState:
        """需求问询节点"""
        return await phase_requirement_inquiry(state)

    async def _catalog_generation_node(self, state: DispatcherState) -> DispatcherState:
        """目录生成节点"""
        return await phase_catalog_generation(state)

    # ... 其他节点实现

    # 路由函数
    def _route_from_catalog(self, state: DispatcherState) -> str:
        """目录生成后的路由"""
        if not state.catalog:
            return "error"
        return "task_assignment"

    def _route_from_drafting(self, state: DispatcherState) -> str:
        """起草后的路由"""
        all_drafted = all(
            ch.status in ["drafted", "reviewed"]
            for ch in state.chapters.values()
        )
        if all_drafted:
            return "final_review"

        pending_review = get_next_pending_review(state.chapters)
        if pending_review:
            return "chapter_review"

        return "next_chapter"

    # ... 其他路由函数
```

### 8.2 ReAct Agent基类实现

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class ReActAgent(BaseAgent):
    """ReAct模式Agent基类"""

    def __init__(self, agent_config: Dict[str, Any]):
        super().__init__(agent_config)
        self.model = self._load_model()
        self.prompt = self._load_prompt()

    def _load_model(self):
        """加载大模型"""
        from langchain_community.llms import OpenAI

        return OpenAI(
            base_url="http://192.168.0.102:8080/v1",
            model="Qwen3.5-35B-A3B-UD-Q4_K_XL",
            temperature=0.7,
            max_tokens=2048
        )

    def _load_prompt(self):
        """加载ReAct提示模板"""
        template = """
你是一个{role}。你的任务是：{task_description}。

你可以使用以下工具：
{tools}

请按照以下格式进行思考和行动：

Thought: 你的思考过程
Action: 工具名称
Action Input: 工具参数
Observation: 工具执行结果
...（重复以上过程）
Thought: 任务完成，结束

开始：
{context}
"""
        return ChatPromptTemplate.from_template(template)

    async def _think(self, **kwargs) -> str:
        """推理过程"""
        context = {
            "role": self.agent_name,
            "task_description": self.get_task_description(),
            "tools": self._format_tools(),
            "context": self._format_context(kwargs)
        }

        chain = self.prompt | self.model | StrOutputParser()
        thought = await chain.ainvoke(context)
        return thought

    def _format_tools(self):
        """格式化工具列表"""
        return "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in self.tools
        ])

    def _format_context(self, kwargs):
        """格式化上下文"""
        # 根据具体Agent实现
        return ""
```

---

## 九、开发计划

### 9.1 开发阶段划分

```
Phase 1: 基础框架搭建（2周）
├─ 项目结构搭建
├─ 数据模型定义
├─ 调度中枢基础框架
├─ ReAct Agent基类
└─ 工具链基础框架

Phase 2: 调度中枢开发（3周）
├─ Planner模块实现
├─ Executor模块实现
├─ Monitor模块实现
├─ State Manager实现
└─ LangGraph状态机实现

Phase 3: 功能Agent开发（4周）
├─ TaskPlannerAgent开发
├─ KnowledgeAgent开发
├─ DraftingAgent开发
├─ ReviewAgent开发
├─ VersionAgent开发
└─ MemberAgent开发

Phase 4: 工具链开发（2周）
├─ 资料检索工具
├─ 规范查询工具
├─ 模型生成工具
├─ 版本管理工具
├─ 用户交互工具
└─ 成员管理工具

Phase 5: 集成测试（2周）
├─ 单元测试
├─ 集成测试
├─ 端到端测试
└─ 性能测试

Phase 6: 部署上线（1周）
├─ Docker容器化
├─ 数据库初始化
├─ 监控告警配置
└─ 生产环境部署
```

### 9.2 技术栈总结

| 组件 | 技术选型 | 用途 |
|------|---------|------|
| Agent框架 | LangGraph | 调度中枢状态机 |
| 后端框架 | Python + FastAPI | API服务 |
| 大模型 | Qwen3.5-35B 本地部署 | 内容生成 |
| 数据存储 | MySQL + MongoDB + Redis | 数据存储 |
| 检索 | Elasticsearch | 全文检索 |
| 知识图谱 | Neo4j | 事实一致性 |
| 容器化 | Docker + Docker Compose | 部署 |

---

## 十、总结

本设计文档明确了县志智能编纂Agent系统的核心架构：

1. **调度中枢（Dispatcher）**：采用Plan and Execute模式，负责全局规划、执行协调、监控调度、状态管理
2. **功能Agent**：采用ReAct模式，负责具体任务执行（需求问询、知识规范、撰稿生成、审校校验、版本控制、成员管理）
3. **协作方式**：通过标准化协议进行任务指令、执行结果、协作调用的传递
4. **完整流程**：9个阶段从需求问询到归档保存的完整闭环
5. **数据模型**：清晰定义了各阶段的数据结构和存储映射

该架构设计遵循分层解耦、模块化、可扩展的原则，为后续开发提供了清晰的指引。
