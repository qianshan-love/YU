"""
成员管理 Agent
负责成员管理、任务重分配
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from src.agents.base_agent import BaseAgent
from src.models.agent import AgentTask, AgentResult
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class MemberAgent(BaseAgent):
    """成员管理Agent"""

    def get_agent_type(self) -> str:
        return "member"

    def _initialize_tools(self) -> List[Any]:
        """初始化工具集"""
        return []

    def get_system_prompt(self) -> str:
        return """你是成员管理专家。你的职责是：
1. 成员管理：添加、删除、更新成员信息
2. 任务重分配：成员变动时重新分配任务
3. 成员查询：查询成员信息、任务分配情况

你会遵循以下原则：
- 确保成员信息的准确性和完整性
- 成员变动时及时重新分配受影响的任务
- 任务分配要考虑成员的专业领域和工作负载
- 保持任务分配的公平性和合理性
"""

    def get_agent_schema(self) -> Dict[str, Any]:
        return {
            "agent_type": "member",
            "agent_name": "成员管理Agent",
            "description": "负责成员管理、任务重分配",
            "actions": [
                "add_member",
                "remove_member",
                "update_member",
                "reassign_tasks"
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

        logger.info(f"[Member] 执行任务: {action}")

        try:
            if action == "add_member":
                return await self._add_member(task)
            elif action == "remove_member":
                return await self._remove_member(task)
            elif action == "update_member":
                return await self._update_member(task)
            elif action == "reassign_tasks":
                return await self._reassign_tasks(task)
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
            logger.error(f"[Member] 执行异常: {str(e)}")
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="failure",
                data={},
                message=f"执行异常: {str(e)}",
                errors=[str(e)]
            )

    async def _add_member(self, task: AgentTask) -> AgentResult:
        """
        添加成员

        Args:
            task: Agent任务

        Returns:
            执行结果
        """
        logger.info("[Member] 添加成员")

        member_info = task.params.get("member_info", {})

        # 简化实现：直接返回成功
        logger.info(f"[Member] 添加成员: {member_info.get('name', '')}")

        return AgentResult(
            task_id=task.task_id,
            agent_type=self.agent_type,
            status="success",
            data={
                "member_info": member_info
            },
            message=f"成员 {member_info.get('name', '')} 添加成功"
        )

    async def _remove_member(self, task: AgentTask) -> AgentResult:
        """
        删除成员

        Args:
            task: Agent任务

        Returns:
            执行结果
        """
        logger.info("[Member] 删除成员")

        member_id = task.params.get("member_id")

        # 简化实现：直接返回成功
        logger.info(f"[Member] 删除成员: {member_id}")

        return AgentResult(
            task_id=task.task_id,
            agent_type=self.agent_type,
            status="success",
            data={
                "member_id": member_id
            },
            message=f"成员 {member_id} 删除成功"
        )

    async def _update_member(self, task: AgentTask) -> AgentResult:
        """
        更新成员信息

        Args:
            task: Agent任务

        Returns:
            执行结果
        """
        logger.info("[Member] 更新成员信息")

        member_id = task.params.get("member_id")
        updates = task.params.get("updates", {})

        # 简化实现：直接返回成功
        logger.info(f"[Member] 更新成员: {member_id}")

        return AgentResult(
            task_id=task.task_id,
            agent_type=self.agent_type,
            status="success",
            data={
                "member_id": member_id,
                "updates": updates
            },
            message=f"成员 {member_id} 更新成功"
        )

    async def _reassign_tasks(self, task: AgentTask) -> AgentResult:
        """
        重新分配任务

        Args:
            task: Agent任务

        Returns:
            执行结果
        """
        logger.info("[Member] 重新分配任务")

        affected_chapters = task.params.get("affected_chapters", [])
        new_assignments = task.params.get("new_assignments", {})

        # 简化实现：直接返回成功
        logger.info(f"[Member] 重新分配任务: {len(affected_chapters)}个章节")

        return AgentResult(
            task_id=task.task_id,
            agent_type=self.agent_type,
            status="success",
            data={
                "affected_chapters": affected_chapters,
                "new_assignments": new_assignments
            },
            message=f"任务重分配完成，共{len(affected_chapters)}个章节"
        )

    # ========== ReAct方法实现 ==========

    async def _think(self, task: AgentTask, iteration: int) -> str:
        """推理过程"""
        action = task.action

        if action == "add_member":
            if iteration == 1:
                return f"我需要添加新成员。"
            else:
                return f"成员添加完成。"

        elif action == "remove_member":
            if iteration == 1:
                return f"我需要删除成员。"
            else:
                return f"成员删除完成。"

        elif action == "update_member":
            if iteration == 1:
                return f"我需要更新成员信息。"
            else:
                return f"成员信息更新完成。"

        elif action == "reassign_tasks":
            if iteration == 1:
                return f"我需要重新分配任务。"
            else:
                return f"任务重分配完成。"

        return "任务完成，结束"

    async def _act(self, thought: str, task: AgentTask) -> tuple:
        """执行行动"""
        # MemberAgent的实际执行在独立方法中
        return None, None

    async def _observe(self, action: str, action_input: Dict[str, Any], task: AgentTask) -> str:
        """观察执行结果"""
        return "任务执行完成"

    async def _finalize(self, task: AgentTask) -> AgentResult:
        """生成最终结果"""
        action = task.action

        if action == "add_member":
            return await self._add_member(task)
        elif action == "remove_member":
            return await self._remove_member(task)
        elif action == "update_member":
            return await self._update_member(task)
        elif action == "reassign_tasks":
            return await self._reassign_tasks(task)
        else:
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="failure",
                data={},
                message=f"未知操作: {action}",
                errors=[f"Unknown action: {action}"]
            )
