"""
Agent基类
定义所有功能Agent的通用接口和行为
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from src.models.agent import (
    AgentTask,
    AgentResult,
    ThoughtActionObservation
)
from src.tools.http_client import get_llm_client
from src.utils.helpers import generate_agent_id
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseAgent(ABC):
    """功能Agent基类"""

    def __init__(self, agent_config: Dict[str, Any]):
        """
        初始化Agent

        Args:
            agent_config: Agent配置
        """
        self.agent_id = agent_config.get("agent_id", generate_agent_id(self.get_agent_type()))
        self.agent_name = agent_config.get("agent_name", self.get_agent_type())
        self.agent_type = self.get_agent_type()
        self.model_config = agent_config.get("model_config", {})
        self.max_iterations = agent_config.get("max_iterations", 10)

        # LLM客户端
        self.llm_client = get_llm_client()

        # 工具集
        self.tools = self._initialize_tools()

        # ReAct历史记录
        self.tao_history: List[ThoughtActionObservation] = []

    @abstractmethod
    def get_agent_type(self) -> str:
        """获取Agent类型"""
        pass

    @abstractmethod
    def _initialize_tools(self) -> List[Any]:
        """初始化工具集"""
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """获取系统提示"""
        pass

    @abstractmethod
    async def execute(self, task: AgentTask) -> AgentResult:
        """执行Agent任务（ReAct循环入口）"""
        pass

    @abstractmethod
    def get_agent_schema(self) -> Dict[str, Any]:
        """获取Agent的Schema定义"""
        pass

    async def run(self, task: AgentTask) -> AgentResult:
        """
        ReAct循环执行

        Args:
            task: Agent任务

        Returns:
            Agent执行结果
        """
        start_time = datetime.now()
        self.tao_history = []

        logger.info(f"[{self.agent_type}] 开始执行任务: {task.action}")
        logger.debug(f"[{self.agent_type}] 任务参数: {task.params}")

        try:
            # 执行ReAct循环
            result = await self._react_loop(task)

            # 计算执行时间
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time

            logger.info(f"[{self.agent_type}] 任务执行完成: {result.status}")
            logger.debug(f"[{self.agent_type}] 执行结果: {result.message}")
            logger.debug(f"[{self.agent_type}] 执行耗时: {execution_time:.2f}秒")

            return result

        except Exception as e:
            # 异常处理
            logger.error(f"[{self.agent_type}] 任务执行异常: {str(e)}")
            execution_time = (datetime.now() - start_time).total_seconds()

            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="failure",
                data={},
                message=f"执行异常: {str(e)}",
                errors=[str(e)],
                execution_time=execution_time
            )

    async def _react_loop(self, task: AgentTask) -> AgentResult:
        """
        ReAct循环主逻辑

        Args:
            task: Agent任务

        Returns:
            执行结果
        """
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1

            # 1. Thought: 推理下一步行动
            thought = await self._think(task, iteration)
            logger.debug(f"[{self.agent_type}] [{iteration}] Thought: {thought}")

            self.tao_history.append(ThoughtActionObservation(
                iteration=iteration,
                thought=thought
            ))

            # 2. 判断是否完成任务
            if self._is_done(thought):
                logger.info(f"[{self.agent_type}] 任务完成，迭代次数: {iteration}")
                return await self._finalize(task)

            # 3. Action: 执行工具调用
            action, action_input = await self._act(thought, task)
            logger.debug(f"[{self.agent_type}] [{iteration}] Action: {action}")

            if action_input:
                logger.debug(f"[{self.agent_type}] [{iteration}] Action Input: {action_input}")

            self.tao_history[-1].action = action
            self.tao_history[-1].action_input = action_input

            # 4. Observation: 获取执行结果
            observation = await self._observe(action, action_input, task)
            logger.debug(f"[{self.agent_type}] [{iteration}] Observation: {observation[:200] if observation else 'None'}...")

            self.tao_history[-1].observation = observation

        # 达到最大迭代次数
        logger.warning(f"[{self.agent_type}] 达到最大迭代次数: {self.max_iterations}")
        return AgentResult(
            task_id=task.task_id,
            agent_type=self.agent_type,
            status="partial",
            data={},
            message=f"达到最大迭代次数({self.max_iterations})",
            execution_time=0
        )

    @abstractmethod
    async def _think(self, task: AgentTask, iteration: int) -> str:
        """
        推理过程

        Args:
            task: 当前任务
            iteration: 当前迭代次数

        Returns:
            思考内容
        """
        pass

    async def _act(self, thought: str, task: AgentTask) -> tuple:
        """
        执行行动

        Args:
            thought: 思考内容
            task: 当前任务

        Returns:
            (action, action_input)
        """
        # 默认实现：从思考中解析行动
        # 子类可以覆盖此方法实现自定义逻辑
        return None, None

    async def _observe(self, action: str, action_input: Dict[str, Any], task: AgentTask) -> str:
        """
        观察执行结果

        Args:
            action: 行动名称
            action_input: 行动输入
            task: 当前任务

        Returns:
            观察结果
        """
        # 默认实现：调用工具
        if action and hasattr(self, f"_tool_{action}"):
            tool_method = getattr(self, f"_tool_{action}")
            try:
                result = await tool_method(action_input or {}, task)
                return str(result)
            except Exception as e:
                logger.error(f"[{self.agent_type}] 工具调用失败: {str(e)}")
                return f"Error: {str(e)}"

        return "No action executed"

    def _is_done(self, thought: str) -> bool:
        """
        判断是否完成

        Args:
            thought: 思考内容

        Returns:
            是否完成
        """
        done_keywords = ["完成", "结束", "done", "finished", "completed", "FINISHED", "DONE"]
        return any(keyword in thought.lower() for keyword in done_keywords)

    async def _finalize(self, task: AgentTask) -> AgentResult:
        """
        生成最终结果

        Args:
            task: Agent任务

        Returns:
            Agent执行结果
        """
        # 子类应该实现此方法来生成具体的结果
        return AgentResult(
            task_id=task.task_id,
            agent_type=self.agent_type,
            status="success",
            data={},
            message="任务完成"
        )

    async def _call_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        调用大模型生成文本

        Args:
            prompt: 提示
            system_prompt: 系统提示
            **kwargs: 其他参数

        Returns:
            生成的文本
        """
        system = system_prompt or self.get_system_prompt()
        return await self.llm_client.generate_text(prompt, system, **kwargs)

    def _format_tools(self) -> str:
        """格式化工具列表（用于提示词）"""
        if not self.tools:
            return "没有可用工具"

        tool_descriptions = []
        for tool in self.tools:
            tool_descriptions.append(f"- {tool.name}: {tool.description}")

        return "\n".join(tool_descriptions)

    def _format_history(self) -> str:
        """格式化历史记录（用于提示词）"""
        if not self.tao_history:
            return ""

        history = []
        for tao in self.tao_history:
            history.append(f"Thought: {tao.thought}")
            if tao.action:
                history.append(f"Action: {tao.action}")
            if tao.observation:
                history.append(f"Observation: {tao.observation}")
            history.append("")

        return "\n".join(history)

    def _get_formatted_prompt(self, task_description: str, context: str = "") -> str:
        """
        获取格式化的提示词

        Args:
            task_description: 任务描述
            context: 上下文

        Returns:
            格式化的提示词
        """
        return f"""{self.get_system_prompt()}

你的任务是：{task_description}

你可以使用以下工具：
{self._format_tools()}

上下文信息：
{context}

历史记录：
{self._format_history()}

请按照以下格式进行思考和行动：

Thought: 你的思考过程
Action: 工具名称
Action Input: 工具参数（JSON格式）
Observation: 工具执行结果
...（重复以上过程）
Thought: 任务完成，结束

开始：
"""
