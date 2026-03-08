"""
调度中枢 Agent
负责全局规划、任务协调、监控调度、状态管理
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import asyncio

from langgraph.graph import StateGraph, END

from src.models.state import (
    DispatcherState, CompilationPhase,
    ChapterInfo, ChapterState, MemberInfo,
    TaskAssignment, VersionInfo, ReviewRecord,
    ContextMessage, ExecutionLog, ErrorInfo
)
from src.models.agent import AgentTask, AgentResult
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DispatcherAgent:
    """调度中枢Agent"""

    def __init__(self):
        """初始化调度中枢"""
        self.agents: Dict[str, Any] = {}  # 功能Agent实例字典
        self.graph = None  # LangGraph状态机

    def register_agent(self, agent_type: str, agent: Any):
        """
        注册功能Agent

        Args:
            agent_type: Agent类型
            agent: Agent实例
        """
        self.agents[agent_type] = agent
        logger.info(f"注册Agent: {agent_type}")

    async def start_compilation(
        self,
        user_id: str,
        initial_requirements: Optional[Dict[str, Any]] = None,
        members: Optional[List[Dict[str, Any]]] = None
    ) -> DispatcherState:
        """
        开始县志编纂任务

        Args:
            user_id: 用户ID
            initial_requirements: 初始需求
            members: 写志组成员

        Returns:
            调度中枢状态
        """
        from src.utils.helpers import generate_task_id

        # 创建初始状态
        state = DispatcherState(
            task_id=generate_task_id(),
            user_id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            current_phase=CompilationPhase.REQUIREMENT_INQUIRY,
            user_requirements=initial_requirements or {},
            members=[MemberInfo(**m) for m in members] if members else []
        )

        logger.info(f"开始编纂任务: {state.task_id}, 用户: {user_id}")
        logger.info(f"当前阶段: {state.current_phase.value}")

        # 构建图（首次）
        if self.graph is None:
            self.graph = self._build_graph()

        # 执行流程
        try:
            # 初始状态需要序列化兼容LangGraph
            state_dict = state.to_dict()
            final_state = await self.graph.ainvoke(state_dict)
            logger.info(f"编纂任务完成: {state.task_id}")

            # 返回更新后的状态
            return self._parse_state(final_state)

        except Exception as e:
            logger.error(f"编纂任务异常: {str(e)}")
            state.errors.append(ErrorInfo(
                error_type="DispatcherError",
                error_message=str(e),
                phase=state.current_phase.value,
                timestamp=datetime.now()
            ))
            state.current_phase = CompilationPhase.ERROR
            return state

    def _build_graph(self) -> StateGraph:
        """
        构建LangGraph状态机

        Returns:
            编译好的状态图
        """
        # 创建状态图
        graph = StateGraph(dict)  # 使用dict作为状态类型

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
        compiled_graph = graph.compile()
        logger.info("LangGraph状态机构建完成")
        return compiled_graph

    # ========== 节点实现 ==========

    async def _requirement_inquiry_node(self, state: dict) -> dict:
        """阶段1：需求问询"""
        from src.models.state import DispatcherState, CompilationPhase

        dispatcher_state = self._parse_state(state)
        logger.info(f"【阶段1】需求问询: {dispatcher_state.task_id}")

        try:
            # 调用TaskPlannerAgent进行需求问询
            task = AgentTask(
                task_id=dispatcher_state.task_id,
                agent_type="task_planner",
                action="inquire_requirements",
                params={
                    "user_id": dispatcher_state.user_id,
                    "initial_requirements": dispatcher_state.user_requirements
                },
                context={}
            )

            result = await self._invoke_agent(task)

            if result.status == "success":
                dispatcher_state.user_requirements = result.data.get("requirements", {})
                dispatcher_state.current_phase = CompilationPhase.CATALOG_GENERATION
                dispatcher_state.updated_at = datetime.now()

                # 记录执行日志
                dispatcher_state.execution_logs.append(ExecutionLog(
                    task_id=dispatcher_state.task_id,
                    agent_type="task_planner",
                    action="inquire_requirements",
                    status="success",
                    message=result.message,
                    execution_time=result.execution_time,
                    timestamp=datetime.now()
                ))

        except Exception as e:
            logger.error(f"需求问询异常: {str(e)}")
            dispatcher_state.errors.append(ErrorInfo(
                error_type="RequirementInquiryError",
                error_message=str(e),
                phase=CompilationPhase.REQUIREMENT_INQUIRY.value,
                timestamp=datetime.now()
            ))

        return dispatcher_state.to_dict()

    async def _catalog_generation_node(self, state: dict) -> dict:
        """阶段2：目录生成"""
        from src.models.state import DispatcherState, CompilationPhase

        dispatcher_state = self._parse_state(state)
        logger.info(f"【阶段2】目录生成: {dispatcher_state.task_id}")

        try:
            task = AgentTask(
                task_id=dispatcher_state.task_id,
                agent_type="task_planner",
                action="generate_catalog",
                params={
                    "user_requirements": dispatcher_state.user_requirements
                },
                context={}
            )

            result = await self._invoke_agent(task)

            if result.status == "success":
                catalog_data = result.data.get("catalog", [])
                dispatcher_state.catalog = [
                    ChapterInfo(**ch) for ch in catalog_data
                ]
                dispatcher_state.total_chapters = len(dispatcher_state.catalog)

                # 初始化章节状态
                for chapter in dispatcher_state.catalog:
                    dispatcher_state.chapters[chapter.chapter_id] = ChapterState(
                        chapter_id=chapter.chapter_id,
                        title=chapter.title,
                        status="pending"
                    )

                dispatcher_state.current_phase = CompilationPhase.TASK_ASSIGNMENT
                dispatcher_state.updated_at = datetime.now()

        except Exception as e:
            logger.error(f"目录生成异常: {str(e)}")
            dispatcher_state.errors.append(ErrorInfo(
                error_type="CatalogGenerationError",
                error_message=str(e),
                phase=CompilationPhase.CATALOG_GENERATION.value,
                timestamp=datetime.now()
            ))

        return dispatcher_state.to_dict()

    async def _task_assignment_node(self, state: dict) -> dict:
        """阶段3：任务分配"""
        from src.models.state import DispatcherState, CompilationPhase

        dispatcher_state = self._parse_state(state)
        logger.info(f"【阶段3】任务分配: {dispatcher_state.task_id}")

        try:
            task = AgentTask(
                task_id=dispatcher_state.task_id,
                agent_type="task_planner",
                action="assign_tasks",
                params={
                    "catalog": [c.__dict__ for c in dispatcher_state.catalog],
                    "members": [m.__dict__ for m in dispatcher_state.members]
                },
                context={}
            )

            result = await self._invoke_agent(task)

            if result.status == "success":
                assignments_data = result.data.get("assignments", {})
                dispatcher_state.task_assignments = {
                    chapter_id: TaskAssignment(**assign)
                    for chapter_id, assign in assignments_data.items()
                }

                # 更新章节分配信息
                for chapter_id, assignment in dispatcher_state.task_assignments.items():
                    if chapter_id in dispatcher_state.chapters:
                        dispatcher_state.chapters[chapter_id].drafters = assignment.drafters
                        dispatcher_state.chapters[chapter_id].reviewers = assignment.reviewers

                dispatcher_state.current_phase = CompilationPhase.CHAPTER_DRAFTING
                dispatcher_state.updated_at = datetime.now()

        except Exception as e:
            logger.error(f"任务分配异常: {str(e)}")
            dispatcher_state.errors.append(ErrorInfo(
                error_type="TaskAssignmentError",
                error_message=str(e),
                phase=CompilationPhase.TASK_ASSIGNMENT.value,
                timestamp=datetime.now()
            ))

        return dispatcher_state.to_dict()

    async def _chapter_drafting_node(self, state: dict) -> dict:
        """阶段4：章节起草（循环执行）"""
        from src.models.state import DispatcherState, CompilationPhase

        dispatcher_state = self._parse_state(state)
        logger.info(f"【阶段4】章节起草: {dispatcher_state.task_id}")

        try:
            # 获取下一个待起草的章节
            next_chapter = self._get_next_pending_chapter(dispatcher_state.chapters)

            if not next_chapter:
                # 所有章节已完成
                logger.info("所有章节起草完成，进入终稿审核")
                dispatcher_state.current_phase = CompilationPhase.FINAL_REVIEW
                return dispatcher_state.to_dict()

            logger.info(f"起草章节: {next_chapter.chapter_id} - {next_chapter.title}")

            # 调用DraftingAgent起草章节
            task = AgentTask(
                task_id=dispatcher_state.task_id,
                agent_type="drafting",
                action="draft_chapter",
                params={
                    "chapter_id": next_chapter.chapter_id,
                    "chapter_title": next_chapter.title,
                    "catalog": [c.__dict__ for c in dispatcher_state.catalog]
                },
                context={
                    "previous_chapters": self._get_previous_chapters(dispatcher_state, next_chapter.chapter_id),
                    "specifications": self._get_chapter_specifications(dispatcher_state, next_chapter.chapter_id)
                }
            )

            result = await self._invoke_agent(task)

            if result.status == "success":
                # 更新章节状态
                chapter_state = dispatcher_state.chapters[next_chapter.chapter_id]
                chapter_state.status = "drafted"
                chapter_state.current_draft = result.data.get("draft")
                chapter_state.word_count = result.data.get("word_count", 0)
                chapter_state.updated_at = datetime.now()

                # 更新版本信息
                version_info = result.data.get("version")
                if version_info:
                    if next_chapter.chapter_id not in dispatcher_state.versions:
                        dispatcher_state.versions[next_chapter.chapter_id] = []
                    dispatcher_state.versions[next_chapter.chapter_id].append(
                        VersionInfo(**version_info)
                    )

                # 添加上下文记忆
                dispatcher_state.context_memory.append(ContextMessage(
                    role="system",
                    content=f"章节{next_chapter.chapter_id}初稿已完成，字数：{result.data.get('word_count', 0)}",
                    timestamp=datetime.now(),
                    metadata={
                        "chapter_id": next_chapter.chapter_id,
                        "version_id": version_info.get("version_id") if version_info else None
                    }
                ))

                logger.info(f"章节 {next_chapter.chapter_id} 起草完成，字数：{result.data.get('word_count', 0)}")

        except Exception as e:
            logger.error(f"章节起草异常: {str(e)}")
            dispatcher_state.errors.append(ErrorInfo(
                error_type="ChapterDraftingError",
                error_message=str(e),
                phase=CompilationPhase.CHAPTER_DRAFTING.value,
                timestamp=datetime.now()
            ))

        return dispatcher_state.to_dict()

    async def _chapter_review_node(self, state: dict) -> dict:
        """阶段5：章节审核"""
        from src.models.state import DispatcherState, CompilationPhase

        dispatcher_state = self._parse_state(state)
        logger.info(f"【阶段5】章节审核: {dispatcher_state.task_id}")

        try:
            # 获取下一个待审核的章节
            next_chapter = self._get_next_pending_review(dispatcher_state.chapters)

            if not next_chapter:
                # 所有章节已审核
                logger.info("所有章节审核完成，进入终稿审核")
                dispatcher_state.current_phase = CompilationPhase.FINAL_REVIEW
                return dispatcher_state.to_dict()

            logger.info(f"审核章节: {next_chapter.chapter_id} - {next_chapter.title}")

            task = AgentTask(
                task_id=dispatcher_state.task_id,
                agent_type="review",
                action="review_chapter",
                params={
                    "chapter_id": next_chapter.chapter_id,
                    "draft": dispatcher_state.chapters[next_chapter.chapter_id].current_draft,
                    "reviewers": dispatcher_state.chapters[next_chapter.chapter_id].reviewers,
                    "versions": [v.__dict__ for v in dispatcher_state.versions.get(next_chapter.chapter_id, [])]
                },
                context={}
            )

            result = await self._invoke_agent(task)

            if result.status == "success":
                # 更新审核记录
                review_record = ReviewRecord(
                    chapter_id=next_chapter.chapter_id,
                    version_id=result.data.get("version_id"),
                    reviewer_id=result.data.get("reviewer_id"),
                    status=result.data.get("status"),
                    comments=result.data.get("comments", ""),
                    timestamp=datetime.now()
                )
                dispatcher_state.review_records.append(review_record)

                # 根据审核结果更新状态
                if result.data.get("status") == "approved":
                    dispatcher_state.chapters[next_chapter.chapter_id].status = "reviewed"
                    logger.info(f"章节 {next_chapter.chapter_id} 审核通过")
                else:
                    dispatcher_state.chapters[next_chapter.chapter_id].status = "pending_revision"
                    dispatcher_state.chapters[next_chapter.chapter_id].review_comments = result.data.get("comments", "")
                    logger.info(f"章节 {next_chapter.chapter_id} 审核驳回")

        except Exception as e:
            logger.error(f"章节审核异常: {str(e)}")
            dispatcher_state.errors.append(ErrorInfo(
                error_type="ChapterReviewError",
                error_message=str(e),
                phase=CompilationPhase.CHAPTER_REVIEW.value,
                timestamp=datetime.now()
            ))

        return dispatcher_state.to_dict()

    async def _draft_revision_node(self, state: dict) -> dict:
        """阶段6：稿件修改"""
        from src.models.state import DispatcherState, CompilationPhase

        dispatcher_state = self._parse_state(state)
        logger.info(f"【阶段6】稿件修改: {dispatcher_state.task_id}")

        try:
            pending_chapter = self._get_pending_revision_chapter(dispatcher_state.chapters)

            if not pending_chapter:
                dispatcher_state.current_phase = CompilationPhase.CHAPTER_DRAFTING
                return dispatcher_state.to_dict()

            logger.info(f"修改章节: {pending_chapter.chapter_id} - {pending_chapter.title}")

            task = AgentTask(
                task_id=dispatcher_state.task_id,
                agent_type="drafting",
                action="revise_chapter",
                params={
                    "chapter_id": pending_chapter.chapter_id,
                    "current_draft": pending_chapter.current_draft,
                    "review_comments": pending_chapter.review_comments,
                    "versions": [v.__dict__ for v in dispatcher_state.versions.get(pending_chapter.chapter_id, [])]
                },
                context={}
            )

            result = await self._invoke_agent(task)

            if result.status == "success":
                # 更新章节状态
                dispatcher_state.chapters[pending_chapter.chapter_id].status = "drafted"
                dispatcher_state.chapters[pending_chapter.chapter_id].current_draft = result.data.get("draft")
                dispatcher_state.chapters[pending_chapter.chapter_id].updated_at = datetime.now()

                # 更新版本
                new_version = result.data.get("version")
                if new_version:
                    dispatcher_state.versions[pending_chapter.chapter_id].append(
                        VersionInfo(**new_version)
                    )

                logger.info(f"章节 {pending_chapter.chapter_id} 修改完成")

        except Exception as e:
            logger.error(f"稿件修改异常: {str(e)}")
            dispatcher_state.errors.append(ErrorInfo(
                error_type="DraftRevisionError",
                error_message=str(e),
                phase=CompilationPhase.DRAFT_REVISION.value,
                timestamp=datetime.now()
            ))

        return dispatcher_state.to_dict()

    async def _final_review_node(self, state: dict) -> dict:
        """阶段7：终稿审核"""
        from src.models.state import DispatcherState, CompilationPhase

        dispatcher_state = self._parse_state(state)
        logger.info(f"【阶段7】终稿审核: {dispatcher_state.task_id}")

        try:
            # 检查是否所有章节都已通过审核
            all_approved = all(
                ch.status == "reviewed"
                for ch in dispatcher_state.chapters.values()
            )

            if not all_approved:
                logger.info("还有章节未通过审核，回到起草阶段")
                dispatcher_state.current_phase = CompilationPhase.CHAPTER_DRAFTING
                return dispatcher_state.to_dict()

            # 整合所有章节为终稿
            task = AgentTask(
                task_id=dispatcher_state.task_id,
                agent_type="drafting",
                action="integrate_final_draft",
                params={
                    "chapters": {k: v.__dict__ for k, v in dispatcher_state.chapters.items()},
                    "catalog": [c.__dict__ for c in dispatcher_state.catalog]
                },
                context={}
            )

            result = await self._invoke_agent(task)

            if result.status == "success":
                dispatcher_state.final_draft = result.data.get("final_draft")
                dispatcher_state.current_phase = CompilationPhase.FINAL_CONFIRMATION
                logger.info("终稿整合完成")

        except Exception as e:
            logger.error(f"终稿审核异常: {str(e)}")
            dispatcher_state.errors.append(ErrorInfo(
                error_type="FinalReviewError",
                error_message=str(e),
                phase=CompilationPhase.FINAL_REVIEW.value,
                timestamp=datetime.now()
            ))

        return dispatcher_state.to_dict()

    async def _final_confirmation_node(self, state: dict) -> dict:
        """阶段8：最终确认"""
        from src.models.state import DispatcherState, CompilationPhase

        dispatcher_state = self._parse_state(state)
        logger.info(f"【阶段8】最终确认: {dispatcher_state.task_id}")

        # TODO: 等待用户确认
        # 这里简化处理，直接确认
        if dispatcher_state.user_requirements.get("confirmed", True):
            dispatcher_state.current_phase = CompilationPhase.ARCHIVING
        else:
            dispatcher_state.current_phase = CompilationPhase.DRAFT_REVISION

        return dispatcher_state.to_dict()

    async def _archiving_node(self, state: dict) -> dict:
        """阶段9：归档保存"""
        from src.models.state import DispatcherState, CompilationPhase

        dispatcher_state = self._parse_state(state)
        logger.info(f"【阶段9】归档保存: {dispatcher_state.task_id}")

        try:
            task = AgentTask(
                task_id=dispatcher_state.task_id,
                agent_type="version",
                action="archive_final_version",
                params={
                    "task_id": dispatcher_state.task_id,
                    "final_draft": dispatcher_state.final_draft,
                    "chapters": {k: v.__dict__ for k, v in dispatcher_state.chapters.items()},
                    "versions": {k: [v.__dict__ for v in v_list] for k, v_list in dispatcher_state.versions.items()},
                    "review_records": [r.__dict__ for r in dispatcher_state.review_records]
                },
                context={}
            )

            result = await self._invoke_agent(task)

            if result.status == "success":
                dispatcher_state.archived = True
                dispatcher_state.archive_info = result.data.get("archive_info")
                dispatcher_state.current_phase = CompilationPhase.COMPLETED
                logger.info("任务归档完成")

        except Exception as e:
            logger.error(f"归档保存异常: {str(e)}")
            dispatcher_state.errors.append(ErrorInfo(
                error_type="ArchivingError",
                error_message=str(e),
                phase=CompilationPhase.ARCHIVING.value,
                timestamp=datetime.now()
            ))

        return dispatcher_state.to_dict()

    async def _error_handler_node(self, state: dict) -> dict:
        """异常处理节点"""
        from src.models.state import DispatcherState

        dispatcher_state = self._parse_state(state)
        logger.error(f"【异常处理】: {dispatcher_state.task_id}")

        dispatcher_state.current_phase = CompilationPhase.ERROR
        dispatcher_state.updated_at = datetime.now()

        return dispatcher_state.to_dict()

    # ========== 路由函数 ==========

    def _route_from_catalog(self, state: dict) -> str:
        """目录生成后的路由"""
        from src.models.state import DispatcherState

        dispatcher_state = self._parse_state(state)

        if not dispatcher_state.catalog or len(dispatcher_state.catalog) == 0:
            return "error"

        return "task_assignment"

    def _route_from_drafting(self, state: dict) -> str:
        """起草后的路由"""
        from src.models.state import DispatcherState

        dispatcher_state = self._parse_state(state)

        # 检查是否所有章节都已完成起草
        all_drafted = all(
            ch.status in ["drafted", "reviewed"]
            for ch in dispatcher_state.chapters.values()
        )

        if all_drafted:
            return "final_review"

        # 检查是否有待审核的章节
        pending_review = self._get_next_pending_review(dispatcher_state.chapters)
        if pending_review:
            return "chapter_review"

        return "next_chapter"

    def _route_from_review(self, state: dict) -> str:
        """审核后的路由"""
        from src.models.state import DispatcherState

        dispatcher_state = self._parse_state(state)

        # 检查是否有待修改的章节
        pending_revision = self._get_pending_revision_chapter(dispatcher_state.chapters)
        if pending_revision:
            return "draft_revision"

        # 检查是否所有章节都已审核通过
        all_reviewed = all(
            ch.status == "reviewed"
            for ch in dispatcher_state.chapters.values()
        )

        if all_reviewed:
            return "final_review"

        return "next_chapter"

    def _route_from_confirmation(self, state: dict) -> str:
        """确认后的路由"""
        from src.models.state import DispatcherState

        dispatcher_state = self._parse_state(state)

        if dispatcher_state.user_requirements.get("confirmed", True):
            return "archiving"

        return "draft_revision"

    # ========== 辅助方法 ==========

    async def _invoke_agent(self, task: AgentTask) -> AgentResult:
        """
        调用功能Agent

        Args:
            task: Agent任务

        Returns:
            执行结果
        """
        agent = self.agents.get(task.agent_type)

        if agent is None:
            logger.error(f"Agent未注册: {task.agent_type}")
            return AgentResult(
                task_id=task.task_id,
                agent_type=task.agent_type,
                status="failure",
                data={},
                message=f"Agent未注册: {task.agent_type}",
                errors=[f"Agent未注册: {task.agent_type}"]
            )

        return await agent.execute(task)

    def _get_next_pending_chapter(self, chapters: Dict[str, Any]) -> Optional[Any]:
        """获取下一个待起草的章节"""
        for chapter in chapters.values():
            if chapter.status == "pending":
                return chapter
        return None

    def _get_next_pending_review(self, chapters: Dict[str, Any]) -> Optional[Any]:
        """获取下一个待审核的章节"""
        for chapter in chapters.values():
            if chapter.status == "drafted":
                return chapter
        return None

    def _get_pending_revision_chapter(self, chapters: Dict[str, Any]) -> Optional[Any]:
        """获取待修改的章节"""
        for chapter in chapters.values():
            if chapter.status == "pending_revision":
                return chapter
        return None

    def _get_previous_chapters(self, state: DispatcherState, chapter_id: str) -> List[str]:
        """获取之前的章节内容（用于上下文）"""
        # 简化实现：返回已完成的章节ID列表
        return [
            ch_id for ch_id, ch in state.chapters.items()
            if ch.status in ["reviewed"] and ch_id != chapter_id
        ]

    def _get_chapter_specifications(self, state: DispatcherState, chapter_id: str) -> Dict[str, Any]:
        """获取章节规范"""
        # 简化实现：返回空字典
        return {}

    def _parse_state(self, state_dict: dict) -> DispatcherState:
        """
        从字典解析状态

        Args:
            state_dict: 状态字典

        Returns:
            DispatcherState对象
        """
        # 简化实现：创建一个基本的状态对象
        # 实际应用中需要完整解析所有字段

        current_phase = state_dict.get("current_phase")
        if isinstance(current_phase, str):
            current_phase = CompilationPhase(current_phase)

        return DispatcherState(
            task_id=state_dict.get("task_id", ""),
            user_id=state_dict.get("user_id", ""),
            created_at=datetime.fromisoformat(state_dict.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(state_dict.get("updated_at", datetime.now().isoformat())),
            current_phase=current_phase,
            user_requirements=state_dict.get("user_requirements", {}),
            members=[MemberInfo(**m) for m in state_dict.get("members", [])],
            task_assignments={
                k: TaskAssignment(**v)
                for k, v in state_dict.get("task_assignments", {}).items()
            },
            chapters={
                k: ChapterState(**v)
                for k, v in state_dict.get("chapters", {}).items()
            },
            versions={
                k: [VersionInfo(**vi) for vi in v]
                for k, v in state_dict.get("versions", {}).items()
            },
            review_records=[ReviewRecord(**r) for r in state_dict.get("review_records", [])],
            context_memory=[
                ContextMessage(**m) for m in state_dict.get("context_memory", [])
            ],
            errors=[
                ErrorInfo(**e) for e in state_dict.get("errors", [])
            ]
        )
