"""
Agent任务和结果模型
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime


@dataclass
class AgentTask:
    """调度中枢发送给功能Agent的任务指令"""
    task_id: str                    # 任务ID
    agent_type: str                 # Agent类型
    action: str                     # 操作类型
    params: Dict[str, Any]          # 参数
    context: Dict[str, Any] = field(default_factory=dict)  # 上下文信息
    priority: int = 1               # 优先级
    timeout: int = 300              # 超时时间(秒)
    created_at: datetime = field(default_factory=datetime.now)


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
    execution_time: float = 0.0     # 执行耗时（秒）
    completed_at: datetime = field(default_factory=datetime.now)


@dataclass
class AgentToAgentRequest:
    """功能Agent之间的协作请求"""
    from_agent: str                 # 来源Agent
    to_agent: str                   # 目标Agent
    request_type: str               # 请求类型
    params: Dict[str, Any]          # 参数
    context: Dict[str, Any] = field(default_factory=dict)  # 上下文


@dataclass
class ThoughtActionObservation:
    """ReAct模式的思考-行动-观察记录"""
    iteration: int                  # 迭代次数
    thought: str                    # 思考内容
    action: Optional[str] = None    # 行动内容
    action_input: Optional[Dict[str, Any]] = None  # 行动输入
    observation: Optional[str] = None  # 观察结果
    timestamp: datetime = field(default_factory=datetime.now)
