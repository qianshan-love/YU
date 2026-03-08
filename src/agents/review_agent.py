"""
审校校验 Agent
负责章节审核、系统校验、终稿审核
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from src.agents.base_agent import BaseAgent
from src.models.agent import AgentTask, AgentResult
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ReviewAgent(BaseAgent):
    """审校校验Agent"""

    def get_agent_type(self) -> str:
        return "review"

    def _initialize_tools(self) -> List[Any]:
        """初始化工具集"""
        return []

    def get_system_prompt(self) -> str:
        return """你是县志审校校验专家。你的职责是：
1. 系统校验：对稿件进行体例、文风、数据格式自动校验
2. 审核管理：管理审核任务，处理审核反馈
3. 终稿审核：审核整合后的终稿

你会遵循以下原则：
- 严格遵循《地方志书质量规定》
- 确保内容真实、准确、可靠
- 语言规范、简练、客观
- 对审核意见要清晰、具体、有可操作性
"""

    def get_agent_schema(self) -> Dict[str, Any]:
        return {
            "agent_type": "review",
            "agent_name": "审校校验Agent",
            "description": "负责章节审核、系统校验、终稿审核",
            "actions": [
                "review_chapter"
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

        logger.info(f"[Review] 执行任务: {action}")

        try:
            if action == "review_chapter":
                return await self._review_chapter(task)
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
            logger.error(f"[Review] 执行异常: {str(e)}")
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="failure",
                data={},
                message=f"执行异常: {str(e)}",
                errors=[str(e)]
            )

    async def _review_chapter(self, task: AgentTask) -> AgentResult:
        """
        章节审核

        Args:
            task: Agent任务

        Returns:
            执行结果
        """
        logger.info("[Review] 开始章节审核")

        chapter_id = task.params.get("chapter_id")
        draft = task.params.get("draft", "")
        reviewers = task.params.get("reviewers", [])
        versions = task.params.get("versions", [])

        # 获取最新版本
        latest_version = versions[-1] if versions else None
        version_id = latest_version.get("version_id") if latest_version else None

        # 系统自动校验
        validation_result = await self._system_validation(chapter_id, draft)

        logger.info(f"[Review] 章节 {chapter_id} 系统校验结果: {validation_result['status']}")

        # 模拟审核结果
        # 实际应用中这里需要推送给审核成员并等待审核结果
        # 这里简化为自动审核通过

        # 如果有审核人，使用第一个审核人的ID
        reviewer_id = reviewers[0] if reviewers else "system"

        # 简化处理：如果系统校验通过，自动审核通过
        if validation_result["status"] == "passed":
            review_status = "approved"
            comments = "系统校验通过，内容符合县志规范。"
        else:
            review_status = "rejected"
            comments = "\n".join(validation_result["errors"])

        logger.info(f"[Review] 章节 {chapter_id} 审核{review_status}")

        return AgentResult(
            task_id=task.task_id,
            agent_type=self.agent_type,
            status="success",
            data={
                "chapter_id": chapter_id,
                "version_id": version_id,
                "reviewer_id": reviewer_id,
                "status": review_status,
                "comments": comments,
                "validation_result": validation_result
            },
            message=f"章节 {chapter_id} 审核{review_status}"
        )

    async def _system_validation(self, chapter_id: str, draft: str) -> Dict[str, Any]:
        """
        系统自动校验

        Args:
            chapter_id: 章节ID
            draft: 稿件内容

        Returns:
            校验结果
        """
        errors = []

        # 简化校验规则
        # 1. 检查字数
        word_count = len(draft)
        if word_count < 500:
            errors.append(f"字数过少（{word_count}字），建议至少1000字。")
        elif word_count > 10000:
            errors.append(f"字数过多（{word_count}字），建议控制在5000字以内。")

        # 2. 检查是否包含禁止词
        forbidden_words = ["我们认为", "我觉得", "可能", "大概", "或许"]
        for word in forbidden_words:
            if word in draft:
                errors.append(f"包含不确定表达 '{word}'，建议删除。")

        # 3. 检查是否有数据引用
        if "数据" in draft and "来源" not in draft:
            errors.append("包含数据引用但未注明来源，请补充数据来源。")

        # 4. 检查结构完整性
        if not any(p in draft for p in ["第一", "首先", "一、", "（一）"]):
            errors.append("文章结构不够清晰，建议使用数字序号组织内容。")

        # 判断校验结果
        if errors:
            return {
                "status": "failed",
                "errors": errors,
                "word_count": word_count
            }
        else:
            return {
                "status": "passed",
                "errors": [],
                "word_count": word_count
            }

    # ========== ReAct方法实现 ==========

    async def _think(self, task: AgentTask, iteration: int) -> str:
        """推理过程"""
        chapter_id = task.params.get("chapter_id")

        if iteration == 1:
            return f"我需要对章节 {chapter_id} 进行审核。"
        elif iteration == 2:
            return f"正在对章节 {chapter_id} 进行系统校验。"
        elif iteration == 3:
            return f"系统校验完成，正在处理审核结果。"
        else:
            return f"章节 {chapter_id} 审核完成。"

    async def _act(self, thought: str, task: AgentTask) -> tuple:
        """执行行动"""
        # ReviewAgent的实际执行在独立方法中
        return None, None

    async def _observe(self, action: str, action_input: Dict[str, Any], task: AgentTask) -> str:
        """观察执行结果"""
        return "任务执行完成"

    async def _finalize(self, task: AgentTask) -> AgentResult:
        """生成最终结果"""
        action = task.action

        if action == "review_chapter":
            return await self._review_chapter(task)
        else:
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="failure",
                data={},
                message=f"未知操作: {action}",
                errors=[f"Unknown action: {action}"]
            )
