"""
撰稿生成 Agent
负责章节起草、稿件修改、终稿整合
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from src.agents.base_agent import BaseAgent
from src.models.agent import AgentTask, AgentResult
from src.models.state import VersionInfo
from src.utils.logger import setup_logger
from src.utils.helpers import generate_version_id

logger = setup_logger(__name__)


class DraftingAgent(BaseAgent):
    """撰稿生成Agent"""

    def get_agent_type(self) -> str:
        return "drafting"

    def _initialize_tools(self) -> List[Any]:
        """初始化工具集"""
        return []

    def get_system_prompt(self) -> str:
        return """你是县志撰稿生成专家。你的职责是：
1. 章节起草：根据目录、规范、资料生成章节内容
2. 稿件修改：根据审核意见修改章节内容
3. 终稿整合：整合所有章节为终稿

你会遵循以下原则：
- 内容符合《地方志书质量规定》
- 语言客观、准确、简练
- 数据真实可靠，有据可查
- 保持县志的严肃性和权威性
"""

    def get_agent_schema(self) -> Dict[str, Any]:
        return {
            "agent_type": "drafting",
            "agent_name": "撰稿生成Agent",
            "description": "负责章节起草、稿件修改、终稿整合",
            "actions": [
                "draft_chapter",
                "revise_chapter",
                "integrate_final_draft"
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

        logger.info(f"[Drafting] 执行任务: {action}")

        try:
            if action == "draft_chapter":
                return await self._draft_chapter(task)
            elif action == "revise_chapter":
                return await self._revise_chapter(task)
            elif action == "integrate_final_draft":
                return await self._integrate_final_draft(task)
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
            logger.error(f"[Drafting] 执行异常: {str(e)}")
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="failure",
                data={},
                message=f"执行异常: {str(e)}",
                errors=[str(e)]
            )

    async def _draft_chapter(self, task: AgentTask) -> AgentResult:
        """
        章节起草

        Args:
            task: Agent任务

        Returns:
            执行结果
        """
        logger.info("[Drafting] 开始章节起草")

        chapter_id = task.params.get("chapter_id")
        chapter_title = task.params.get("chapter_title")
        catalog = task.params.get("catalog", [])
        context = task.context

        # 构建起草提示词
        previous_chapters = context.get("previous_chapters", [])
        specifications = context.get("specifications", {})

        previous_context = ""
        if previous_chapters:
            previous_context = f"前序章节已完成: {', '.join(previous_chapters)}\n"

        prompt = f"""请撰写县志章节内容：

章节编号：{chapter_id}
章节标题：{chapter_title}

{previous_context}
县志目录结构：
{self._format_catalog(catalog)}

撰写要求：
1. 内容符合县志规范，语言客观、准确、简练
2. 数据真实可靠，有据可查
3. 结构清晰，逻辑严密
4. 字数控制在3000-5000字

请直接返回章节内容，不要包含任何标题前缀或说明文字。"""

        draft_content = await self._call_llm(prompt, max_tokens=5000)

        word_count = len(draft_content)

        logger.info(f"[Drafting] 章节 {chapter_id} 起草完成，字数：{word_count}")

        # 生成版本信息
        version_number = 1
        version_id = generate_version_id(chapter_id, version_number)

        version_info = VersionInfo(
            version_id=version_id,
            chapter_id=chapter_id,
            version_number=version_number,
            content=draft_content,
            created_by=self.agent_id,
            created_at=datetime.now(),
            version_type="initial",
            status="active",
            diff=None
        )

        return AgentResult(
            task_id=task.task_id,
            agent_type=self.agent_type,
            status="success",
            data={
                "chapter_id": chapter_id,
                "draft": draft_content,
                "word_count": word_count,
                "version": {
                    "version_id": version_id,
                    "chapter_id": chapter_id,
                    "version_number": version_number,
                    "content": draft_content,
                    "created_by": self.agent_id,
                    "created_at": datetime.now().isoformat(),
                    "version_type": "initial",
                    "status": "active",
                    "diff": None
                }
            },
            message=f"章节 {chapter_id} 起草完成"
        )

    async def _revise_chapter(self, task: AgentTask) -> AgentResult:
        """
        稿件修改

        Args:
            task: Agent任务

        Returns:
            执行结果
        """
        logger.info("[Drafting] 开始稿件修改")

        chapter_id = task.params.get("chapter_id")
        current_draft = task.params.get("current_draft")
        review_comments = task.params.get("review_comments", "")
        versions = task.params.get("versions", [])

        # 获取上一版本号
        version_number = len(versions) + 1

        prompt = f"""请根据审核意见修改以下县志章节内容：

章节编号：{chapter_id}

当前内容：
{current_draft}

审核意见：
{review_comments}

修改要求：
1. 根据审核意见进行修改
2. 保持县志规范的严肃性和客观性
3. 确保修改后的内容真实、准确
4. 保持文章结构的完整性

请直接返回修改后的章节内容，不要包含任何标题前缀或说明文字。"""

        revised_content = await self._call_llm(prompt, max_tokens=5000)

        word_count = len(revised_content)

        logger.info(f"[Drafting] 章节 {chapter_id} 修改完成，字数：{word_count}")

        # 生成版本信息
        version_id = generate_version_id(chapter_id, version_number)

        version_info = VersionInfo(
            version_id=version_id,
            chapter_id=chapter_id,
            version_number=version_number,
            content=revised_content,
            created_by=self.agent_id,
            created_at=datetime.now(),
            version_type="revised",
            status="active",
            diff=self._generate_diff(current_draft, revised_content)
        )

        return AgentResult(
            task_id=task.task_id,
            agent_type=self.agent_type,
            status="success",
            data={
                "chapter_id": chapter_id,
                "draft": revised_content,
                "word_count": word_count,
                "version": {
                    "version_id": version_id,
                    "chapter_id": chapter_id,
                    "version_number": version_number,
                    "content": revised_content,
                    "created_by": self.agent_id,
                    "created_at": datetime.now().isoformat(),
                    "version_type": "revised",
                    "status": "active",
                    "diff": version_info.diff
                }
            },
            message=f"章节 {chapter_id} 修改完成"
        )

    async def _integrate_final_draft(self, task: AgentTask) -> AgentResult:
        """
        终稿整合

        Args:
            task: Agent任务

        Returns:
            执行结果
        """
        logger.info("[Drafting] 开始终稿整合")

        chapters = task.params.get("chapters", {})
        catalog = task.params.get("catalog", [])

        # 按目录顺序整合章节
        final_draft_parts = []

        for chapter_info in catalog:
            chapter_id = chapter_info.get("chapter_id")
            chapter = chapters.get(chapter_id)

            if chapter and chapter.get("current_draft"):
                # 添加章节标题
                title = chapter_info.get("title", chapter_id)
                final_draft_parts.append(f"# {title}")
                final_draft_parts.append("")
                final_draft_parts.append(chapter.get("current_draft"))
                final_draft_parts.append("")
                final_draft_parts.append("---")
                final_draft_parts.append("")

        final_draft = "\n".join(final_draft_parts)
        word_count = len(final_draft)

        logger.info(f"[Drafting] 终稿整合完成，字数：{word_count}")

        return AgentResult(
            task_id=task.task_id,
            agent_type=self.agent_type,
            status="success",
            data={
                "final_draft": final_draft,
                "word_count": word_count,
                "total_chapters": len(catalog)
            },
            message=f"终稿整合完成，共{len(catalog)}章"
        )

    def _format_catalog(self, catalog: List[Dict[str, Any]]) -> str:
        """格式化目录"""
        return "\n".join([
            f"{ch.get('chapter_id')}: {ch.get('title')}"
            for ch in catalog
        ])

    def _generate_diff(self, old_content: str, new_content: str) -> str:
        """生成内容差异（简化版本）"""
        # 简化实现：返回版本号
        return "内容已更新"

    # ========== ReAct方法实现 ==========

    async def _think(self, task: AgentTask, iteration: int) -> str:
        """推理过程"""
        action = task.action
        chapter_id = task.params.get("chapter_id")

        if action == "draft_chapter":
            if iteration == 1:
                return f"我需要根据目录和规范为章节 {chapter_id} 撰写内容。"
            elif iteration == 2:
                return f"正在为章节 {chapter_id} 生成内容。"
            else:
                return f"章节 {chapter_id} 起草完成。"

        elif action == "revise_chapter":
            if iteration == 1:
                return f"我需要根据审核意见修改章节 {chapter_id}。"
            elif iteration == 2:
                return f"正在修改章节 {chapter_id}。"
            else:
                return f"章节 {chapter_id} 修改完成。"

        elif action == "integrate_final_draft":
            if iteration == 1:
                return f"我需要整合所有章节为终稿。"
            elif iteration == 2:
                return f"正在整合各章节内容。"
            else:
                return f"终稿整合完成。"

        return "任务完成，结束"

    async def _act(self, thought: str, task: AgentTask) -> tuple:
        """执行行动"""
        # DraftingAgent的实际执行在各个独立方法中
        return None, None

    async def _observe(self, action: str, action_input: Dict[str, Any], task: AgentTask) -> str:
        """观察执行结果"""
        return "任务执行完成"

    async def _finalize(self, task: AgentTask) -> AgentResult:
        """生成最终结果"""
        action = task.action

        if action == "draft_chapter":
            return await self._draft_chapter(task)
        elif action == "revise_chapter":
            return await self._revise_chapter(task)
        elif action == "integrate_final_draft":
            return await self._integrate_final_draft(task)
        else:
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="failure",
                data={},
                message=f"未知操作: {action}",
                errors=[f"Unknown action: {action}"]
            )
