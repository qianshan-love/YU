"""
调度中枢状态模型
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class CompilationPhase(str, Enum):
    """编纂阶段枚举"""
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


@dataclass
class ChapterInfo:
    """章节信息"""
    chapter_id: str                    # 章节ID
    title: str                          # 章节标题
    level: int                          # 章节层级（1=卷，2=篇，3=章，4=节）
    parent_id: Optional[str] = None    # 父章节ID
    order: int = 0                      # 排序
    word_count: int = 0                # 预计字数


@dataclass
class ChapterState:
    """章节状态"""
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


@dataclass
class MemberInfo:
    """成员信息"""
    member_id: str                      # 成员ID
    name: str                           # 姓名
    role: str                           # 角色：editor/reviewer/admin
    expertise: List[str] = field(default_factory=list)  # 专业领域
    workload: int = 0                   # 当前工作负载


@dataclass
class TaskAssignment:
    """任务分配"""
    chapter_id: str                    # 章节ID
    drafters: List[str]                 # 撰稿人列表
    reviewers: List[str]                # 审核人列表
    priority: int = 1                   # 优先级
    deadline: Optional[datetime] = None # 截止时间


@dataclass
class VersionInfo:
    """版本信息"""
    version_id: str                    # 版本ID
    chapter_id: str                    # 章节ID
    version_number: int                # 版本号
    content: str                       # 版本内容
    created_by: str                     # 创建者（Agent ID）
    created_at: datetime               # 创建时间
    version_type: str                  # 版本类型：initial/revised/final
    status: str                        # 状态：active/archived
    diff: Optional[str] = None         # 与上一版本的差异


@dataclass
class ReviewRecord:
    """审核记录"""
    chapter_id: str                    # 章节ID
    version_id: str                    # 版本ID
    reviewer_id: str                   # 审核人ID
    status: str                        # 状态：approved/rejected
    comments: str                      # 审核意见
    timestamp: datetime                # 审核时间


@dataclass
class ContextMessage:
    """上下文消息"""
    role: str                          # 角色：system/user/assistant
    content: str                       # 消息内容
    timestamp: datetime                # 时间戳
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据


@dataclass
class ExecutionLog:
    """执行日志"""
    task_id: str                       # 任务ID
    agent_type: str                    # Agent类型
    action: str                        # 操作
    status: str                        # 状态：success/failure/pending
    message: str                       # 消息
    execution_time: float              # 执行耗时（秒）
    timestamp: datetime                # 时间戳


@dataclass
class ErrorInfo:
    """异常信息"""
    error_type: str                    # 错误类型
    error_message: str                 # 错误消息
    phase: str                         # 发生阶段
    agent_type: Optional[str] = None    # 关联Agent
    stack_trace: Optional[str] = None   # 堆栈信息
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MemberChangeEvent:
    """成员变动事件"""
    event_type: str                    # 事件类型：added/removed/updated
    member_id: str                     # 成员ID
    old_info: Optional[MemberInfo] = None  # 旧信息
    new_info: Optional[MemberInfo] = None  # 新信息
    affected_tasks: List[str] = field(default_factory=list)  # 受影响的任务
    timestamp: datetime = field(default_factory=datetime.now)


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
    previous_phase: Optional[CompilationPhase] = None # 上一阶段
    phase_history: List[CompilationPhase] = field(default_factory=list)  # 阶段历史记录

    # ============ 用户需求 ============
    user_requirements: Dict[str, Any] = field(default_factory=dict)  # 用户原始需求
    county_info: Dict[str, Any] = field(default_factory=dict)      # 县志背景信息
    compilation_purpose: str = ""                          # 编纂目的
    time_range: Optional[tuple] = None                # 时间范围

    # ============ 目录结构 ============
    catalog: List[ChapterInfo] = field(default_factory=list)  # 县志目录结构
    total_chapters: int = 0                              # 总章节数

    # ============ 成员管理 ============
    members: List[MemberInfo] = field(default_factory=list)  # 写志组成员
    member_changes: List[MemberChangeEvent] = field(default_factory=list)  # 成员变动记录

    # ============ 任务分配 ============
    task_assignments: Dict[str, TaskAssignment] = field(default_factory=dict)  # 任务分配映射

    # ============ 章节状态 ============
    chapters: Dict[str, ChapterState] = field(default_factory=dict)  # 章节状态字典

    # ============ 版本管理 ============
    versions: Dict[str, List[VersionInfo]] = field(default_factory=dict)  # 版本信息
    final_draft: Optional[str] = None               # 终稿内容

    # ============ 审核记录 ============
    review_records: List[ReviewRecord] = field(default_factory=list)  # 审核记录列表

    # ============ 上下文记忆 ============
    context_memory: List[ContextMessage] = field(default_factory=list)  # 上下文记忆
    execution_logs: List[ExecutionLog] = field(default_factory=list)  # 执行日志

    # ============ 异常与状态 ============
    errors: List[ErrorInfo] = field(default_factory=list)  # 异常记录
    retry_count: int = 0                             # 重试次数
    is_paused: bool = False                          # 是否暂停
    is_terminated: bool = False                       # 是否终止

    # ============ 归档信息 ============
    archived: bool = False                           # 是否已归档
    archive_info: Optional[Dict[str, Any]] = None    # 归档信息

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于序列化）"""
        return {
            "task_id": self.task_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "current_phase": self.current_phase.value,
            "previous_phase": self.previous_phase.value if self.previous_phase else None,
            "phase_history": [p.value for p in self.phase_history],
            "user_requirements": self.user_requirements,
            "county_info": self.county_info,
            "compilation_purpose": self.compilation_purpose,
            "time_range": self.time_range,
            "catalog": [{"chapter_id": c.chapter_id, "title": c.title, "level": c.level, "order": c.order} for c in self.catalog],
            "total_chapters": self.total_chapters,
            "members": [{"member_id": m.member_id, "name": m.name, "role": m.role} for m in self.members],
            "task_assignments": {k: {"chapter_id": v.chapter_id, "drafters": v.drafters, "reviewers": v.reviewers} for k, v in self.task_assignments.items()},
            "chapters": {k: {"chapter_id": v.chapter_id, "title": v.title, "status": v.status} for k, v in self.chapters.items()},
            "versions": {k: [{"version_id": vi.version_id, "version_number": vi.version_number} for vi in v] for k, v in self.versions.items()},
            "review_records": [{"chapter_id": r.chapter_id, "status": r.status} for r in self.review_records],
            "errors": [{"error_type": e.error_type, "error_message": e.error_message} for e in self.errors],
            "retry_count": self.retry_count,
            "is_paused": self.is_paused,
            "is_terminated": self.is_terminated,
            "archived": self.archived
        }
