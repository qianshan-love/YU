# 县志智能编纂Agent系统

## 📋 项目概述

基于LangGraph和ReAct模式的县志智能编纂系统，实现全流程自动化编纂、上下文长记忆留存、对话样本结构化存储。

## 🎯 核心特性

- **Plan and Execute模式调度中枢**：全局规划、执行协调、监控调度、状态管理
- **ReAct模式功能Agent**：6个功能Agent，各司其职，灵活应变
- **Agent托管式版本控制**：用户零操作，Agent全自动管理版本
- **完整工作流程**：9个阶段从需求问询到归档保存的完整闭环

## 🏗️ 当前项目结构

```
county-chronicles-agent/
├── config/                    # 配置文件
│   └── settings.py           # 项目配置
├── data/                     # 数据存储（待实现）
│   ├── knowledge_base/          # 知识库数据
│   ├── versions/              # 版本数据
│   └── execution_logs/        # 执行日志
├── src/
│   ├── agents/              # Agent模块 ✅
│   │   ├── __init__.py
│   │   ├── base_agent.py    # Agent基类 ✅
│   │   ├── dispatcher.py    # 调度中枢 ✅
│   │   ├── task_planner_agent.py   # 任务规划Agent ✅
│   │   ├── drafting_agent.py       # 撰稿生成Agent ✅
│   │   ├── review_agent.py         # 审校校验Agent ✅
│   │   ├── version_agent.py         # 版本控制Agent ✅
│   │   └── member_agent.py         # 成员管理Agent ✅
│   ├── models/              # 数据模型 ✅
│   │   ├── __init__.py
│   │   ├── state.py        # 状态模型 ✅
│   │   └── agent.py        # Agent模型 ✅
│   └── tools/               # 工具模块 ✅
│       ├── content_generation.py  # 内容生成 ✅
│       ├── http_client.py  # HTTP客户端（LLM调用） ✅
│       ├── llm_service.py      # LLM服务 ✅
│       ├── retrieval.py        # 知识检索 ✅
│       ├── specification.py    # 规范查询 ✅
│       ├── system_validation.py # 系统校验 ✅
│       ├── user_interaction.py # 用户交互 ✅
│       ├── version_manager.py  # 版本管理 ✅
│       └── web_search.py      # 网络搜索 ✅
│   └── utils/               # 工具函数 ✅
│       ├── __init__.py
│       ├── logger.py        # 日志工具 ✅
│       └── helpers.py       # 辅助函数 ✅
├── debug_interface_optimized.py  # 调试界面（优化版） ✅
├── main.py                  # 主入口 ✅
├── requirements.txt         # 依赖包 ✅
├── .env.example            # 环境变量示例 ✅
├── DESIGN.md               # 设计文档 ✅
├── IMPLEMENTATION_SUMMARY.md  # 实现总结 ✅
├── DEBUG_INTERFACE_GUIDE.md # 调试界面指南 ✅
└── PROJECT_STATUS.md       # 项目状态文档 ✅（本文件）
```

## 🤖 Agent架构

### 调度中枢 Agent (Dispatcher) ✅
- **功能**：全局规划、任务协调、状态管理、监控调度
- **设计模式**：Plan and Execute
- **实现进度**：90%
- **主要功能**：任务分配、Agent调度、状态机管理

### 功能执行Agent (6个)

#### 1. 任务规划 Agent (TaskPlannerAgent) ✅
- **功能**：需求问询、目录生成、任务分配
- **设计模式**：ReAct
- **实现进度**：65%
- **依赖工具**：内容生成、用户交互

#### 2. 知识规范 Agent (KnowledgeAgent) ✅
- **功能**：规范查询、知识检索、网络搜索、规范校验
- **设计模式**：ReAct
- **实现进度**：75%
- **依赖工具**：规范查询、知识检索、网络搜索

#### 3. 撰稿生成 Agent (DraftingAgent) ✅
- **功能**：章节起草、内容生成、版本管理
- **设计模式**：ReAct
- **实现进度**：60%
- **依赖工具**：内容生成、版本管理、系统校验

#### 4. 审校校验 Agent (ReviewAgent) ✅
- **功能**：系统校验、人工审核、版本对比、事实一致性检查
- **设计模式**：ReAct
- **实现进度**：50%
- **依赖工具**：系统校验、版本对比

#### 5. 版本控制 Agent (VersionAgent) ✅
- **功能**：版本生成、查询、对比、回退、归档
- **设计模式**：ReAct
- **实现进度**：55%
- **依赖工具**：版本管理

#### 6. 成员管理 Agent (MemberAgent) ✅
- **功能**：成员管理、任务重分配、通知发送
- **设计模式**：ReAct
- **实现进度**：50%
- **依赖工具**：用户交互

## 🛠️ 工具层

### 已实现工具（7个）

#### 1. 大模型服务 ✅
- **文件**：`src/tools/llm_service.py`
- **功能**：封装Qwen3.5-35B模型调用
- **特性**：对话、文本生成、流式输出、工具调用支持
- **配置**：http://140.143.163.123:59655/v1/chat/completions

#### 2. 内容生成工具 ✅
- **文件**：`src/tools/content_generation.py`
- **功能**：章节生成、目录生成、小节生成、内容改进
- **集成**：使用LLM服务

#### 3. 版本管理工具 ✅
- **文件**：`src/tools/version_manager.py`
- **功能**：版本CRUD、版本对比、版本回退、版本归档
- **实现**：内存存储（实际项目应使用数据库）

#### 4. 用户交互工具 ✅
- **文件**：`src/tools/user_interaction.py`
- **功能**：用户问答、需求问询、通知发送、问题历史管理

#### 5. 系统校验工具 ✅
- **文件**：`src/tools/system_validation.py`
- **功能**：体例校验、格式校验、事实校验
- **规则**：预设校验规则（体例、格式、事实）

#### 6. 网络搜索工具 ✅
- **文件**：`src/tools/web_search.py`
- **功能**：多数据源支持（seesea、bing、google、mock）
- **当前状态**：seesea因Windows权限问题使用mock数据
- **降级机制**：seesea → bing → google → mock

#### 7. 规范查询工具 ✅
- **文件**：`src/tools/specification.py`
- **功能**：县志规范查询和内容校验
- **支持**：章节规范、撰写规范、体例规范

## 🔧 调试和测试工具

### 调试界面 ✅
- **文件**：`debug_interface_optimized.py`
- **功能**：
  - Agent工作状态实时监控（6个Agent）
  - 大模型对话测试
  - 系统日志实时查看
  - Agent功能快速测试
  - 自动状态刷新（10秒间隔）
- **访问**：http://localhost:8001

### 主要文档

| 文档 | 说明 | 状态 |
|------|------|------|
| DESIGN.md | 系统架构设计文档 | ✅ 完成 |
| IMPLEMENTATION_SUMMARY.md | 实现工作总结 | ✅ 完成 |
| DEBUG_INTERFACE_GUIDE.md | 调试界面使用指南 | ✅ 完成 |
| PROJECT_STATUS.md | 项目状态总览 | ✅ 完成 |

## 📊 技术栈

### 核心技术
- **Agent框架**：LangGraph (调度中枢) + ReAct (功能Agent)
- **大模型**：Qwen3.5-35B-A3B-UD-Q4_K_XL
- **后端框架**：FastAPI
- **异步处理**：asyncio
- **日志系统**：自定义日志系统
- **配置管理**：环境变量配置

### 开发语言
- **Python版本**：3.13+
- **主要依赖**：httpx、fastapi、uvicorn、langgraph

### 网络请求
- **LLM API**：http://140.143.163.123:59655/v1/chat/completions
- **数据源**：seesea（国内）→ Bing API → Google API → mock

## 🚀 快速开始

### 1. 启动调试界面
```bash
python debug_interface_optimized.py
```

### 2. 访问调试界面
打开浏览器访问：http://localhost:8001

### 3. 测试大模型
在调试界面的"大模型对话测试"区域测试Qwen3.5-35B模型调用

### 4. 查看项目状态
参考 `PROJECT_STATUS.md` 了解当前项目完成度和待完成工作

## 📝 环境配置

### 创建环境变量文件
```bash
cp .env.example .env
```

### 基础配置
```bash
# 大模型配置（已配置在代码中）
LLM_API_URL=http://140.143.163.123:59655/v1/chat/completions
LLM_MODEL_NAME=Qwen3.5-35B-A3B-UD-Q4_K_XL

# 搜索API配置（可选）
USE_SEASEA=false
SEASEA_DEFAULT_ENGINE=baidu
BING_API_KEY=
GOOGLE_API_KEY=
GOOGLE_SEARCH_ENGINE_ID=
```

## 🎯 开发路线图

### 阶段1：核心功能开发（已完成60%）
- ✅ Agent框架和调度中枢
- ✅ 大模型集成
- ✅ 基础工具实现
- ⏳ Agent工具集成
- ⏳ 数据库实现

### 阶段2：数据层实现（待开发）
- ⏳ MySQL配置和表结构
- ⏳ MongoDB配置和存储
- ⏳ Redis缓存配置
- ⏳ 数据访问层（DAO）

### 阶段3：完善和优化（待开发）
- ⏳ Agent功能完善
- ⏳ 规则引擎扩展
- ⏳ 性能优化
- ⏳ 错误处理完善

### 阶段4：测试和部署（待开发）
- ⏳ 端到端测试
- ⏳ 性能测试
- ⏳ 生产环境部署

## 📈 项目完成度统计

| 模块 | 完成度 | 文件数 | 代码行数（估算） |
|------|--------|----------|------------------|
| Agent框架 | 90% | 7 | ~2000行 |
| 功能Agent | 60% | 6 | ~1900行 |
| 工具层 | 70% | 7 | ~2200行 |
| 调试界面 | 100% | 1 | ~800行 |
| 数据层 | 0% | 0 | 0行 |
| 文档 | 90% | 4 | ~1500行 |
| **总体** | **60%** | **25** | **~8400行** |

## 🤝 版本控制

**仓库地址**：`git@github.com:qianshan-love/YU.git`

**分支**：`main`

**主要分支说明**：
- `main`：稳定开发分支，包含当前所有完成的功能
- 建议为不同功能创建特性分支进行开发

---

## 🔗️ 项目架构说明

### 调度流程
```
用户需求 → TaskPlannerAgent（规划） → Dispatcher（调度）
    ↓
DraftingAgent（撰写） → VersionAgent（版本管理） → ReviewAgent（审核）
    ↓
KnowledgeAgent（知识支撑） → 所有Agent
```

### Agent协作模式
- **调度中枢**使用LangGraph进行状态管理和任务编排
- **功能Agent**使用ReAct模式进行工具调用和推理
- **Agent间通信**通过Dispatcher进行任务分配和数据传递

---

**当前项目状态：核心架构完成约60%，工具层完成约70%，可以进行Agent集成和数据库开发！**
