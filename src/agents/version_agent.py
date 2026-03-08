"""
版本控制 Agent
负责版本生成、查询、对比、回退、归档
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from src.agents.base_agent import BaseAgent
from src.models.agent import AgentTask, AgentResult
from src.models.state import VersionInfo
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class VersionAgent(BaseAgent):
    """版本控制Agent"""

    def get_agent_type(self) -> str:
        return "version"

    def _initialize_tools(self) -> List[Any]:
        """初始化工具集"""
        return []

    def get_system_prompt(self) -> str:
        return """你是版本管理专家。你的职责是：
1. 版本生成：自动生成版本号、保存版本内容
2. 版本查询：查询历史版本
3. 版本对比：对比不同版本内容
4. 版本回退：回退到指定版本
5. 版本归档：归档终稿版本

你会遵循以下原则：
- 确保版本号的唯一性和连续性
- 完整保存每个版本的内容
- 提供清晰的版本对比功能
- 保证版本数据的安全性和可靠性
"""

    def get_agent_schema(self) -> Dict[str, Any]:
        return {
            "agent_type": "version",
            "agent_name": "版本控制Agent",
            "description": "负责版本生成、查询、对比、回退、归档",
            "actions": [
                "archive_final_version"
            ]
        }

    async def execute(self, task: AgentTask) -> AgentResult:
        """
        执行Agent任务

        Args:
            task: Agent任务

        Returns:
            Agent执行结果
        """
        action = task.action
        params = task.params

        logger.info(f"[Version] 执行任务: {action}")

        try:
            if action == "archive_final_version":
                return await self._archive_final_version(task)
            else:
                return AgentResult(
                    task_id=task.task_id,
                    agent_type=self.agent_type,
                    status="failure",
                    data={},
                    message=f"未知操作: {action}",
                    errors=[f"Unknown action: {action}"]
                )

        except Exception as e:
            logger.error(f"[Version] 执行异常: {str(e)}")
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="failure",
                data={},
                message=f"执行异常: {str(e)}",
                errors=[str(e)]
            )

    async def _archive_final_version(self, task: AgentTask) -> AgentResult:
        """
        归档终稿版本

        Args:
            task: Agent任务

        Returns:
            执行结果
        """
        logger.info("[Version] 开始终稿归档")

        task_id = task.params.get("task_id")
        final_draft = task.params.get("final_draft")
        chapters = task.params.get("chapters", {})
        versions = task.params.get("versions", {})
        review_records = task.params.get("review_records", [])

        # 生成归档信息
        archive_info = {
            "task_id": task_id,
            "archived_at": datetime.now().isoformat(),
            "archived_by": self.agent_id,
            "total_chapters": len(chapters),
            "total_words": len(final_draft),
            "total_versions": sum(len(v) for v in versions.values()),
            "total_reviews": len(review_records),
            "status": "completed"
        }

        logger.info(f"[Version] 终稿归档完成: {archive_info}")

        return AgentResult(
            task_id=task.task_id,
            agent_type=self.agent_type,
            status="success",
            data={
                "archive_info": archive_info
            },
            message=f"终稿归档完成，共{len(chapters)}章，{archive_info['total_words']}字"
        )

    # ========== ReAct方法实现 ==========

    async def _think(self, task: AgentTask, iteration: int) -> str:
        """推理过程"""
        action = task.action

        if action == "archive_final_version":
            if iteration == 1:
                return f"我需要归档终稿版本。"
            elif iteration == 2:
                return f"正在整理版本数据和审核记录。"
            else:
                return f"终稿归档完成。"

        return "任务完成，结束"

    async def _act(self, thought: str, task: AgentTask) -> tuple:
        """执行行动"""
        # VersionAgent的实际执行在独立方法中
        return None, None

    async def _observe(self, action: str, action_input: Dict[str, Any], task: AgentTask) -> str:
        """观察执行结果"""
        return "任务执行完成"

    async def _finalize(self, task: AgentTask) -> AgentResult:
        """生成最终结果"""
        action = task.action

        if action == "archive_final_version":
            return await self._archive_final_version(task)
        else:
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="failure",
                data={},
                message=f"未知操作: {action}",
                errors=[f"Unknown action: {action}"]
            )
