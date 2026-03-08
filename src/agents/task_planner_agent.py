"""
任务规划 Agent
负责需求问询、目录生成、任务分配
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from src.agents.base_agent import BaseAgent
from src.models.agent import AgentTask, AgentResult, ThoughtActionObservation
from src.models.state import ChapterInfo, TaskAssignment
from src.utils.logger import setup_logger
from src.utils.helpers import generate_version_id

logger = setup_logger(__name__)


class TaskPlannerAgent(BaseAgent):
    """任务规划Agent"""

    def get_agent_type(self) -> str:
        return "task_planner"

    def _initialize_tools(self) -> List[Any]:
        """初始化工具集"""
        return []

    def get_system_prompt(self) -> str:
        return """你是县志编纂任务规划专家。你的职责是：
1. 需求问询：向用户询问编纂背景、目的、范围等信息
2. 目录生成：基于用户需求生成符合国标的县志目录结构
3. 任务分配：根据成员数量合理分配撰稿和审核任务

你会遵循以下原则：
- 目录结构符合《地方志书质量规定》
- 任务分配考虑成员的专业领域和工作负载
- 与用户交互时要礼貌、专业、准确
"""

    def get_agent_schema(self) -> Dict[str, Any]:
        return {
            "agent_type": "task_planner",
            "agent_name": "任务规划Agent",
            "description": "负责需求问询、目录生成、任务分配",
            "actions": [
                "inquire_requirements",
                "generate_catalog",
                "assign_tasks"
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

        logger.info(f"[TaskPlanner] 执行任务: {action}")

        try:
            if action == "inquire_requirements":
                return await self._inquire_requirements(task)
            elif action == "generate_catalog":
                return await self._generate_catalog(task)
            elif action == "assign_tasks":
                return await self._assign_tasks(task)
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
            logger.error(f"[TaskPlanner] 执行异常: {str(e)}")
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="failure",
                data={},
                message=f"执行异常: {str(e)}",
                errors=[str(e)]
            )

    async def _inquire_requirements(self, task: AgentTask) -> AgentResult:
        """
        需求问询

        Args:
            task: Agent任务

        Returns:
            执行结果
        """
        logger.info("[TaskPlanner] 开始需求问询")

        initial_requirements = task.params.get("initial_requirements", {})
        user_id = task.params.get("user_id", "")

        # 构建问询提示词
        if not initial_requirements:
            # 首次问询
            prompt = """请向用户询问县志编纂的基本信息，包括：
1. 县志编纂的县级行政区名称
2. 编纂目的（例如：续修、重修、增修等）
3. 时间范围（起止年份）
4. 编纂类型（例如：综合志、专业志等）
5. 特殊要求或关注重点

请用礼貌、专业的方式组织问题。"""

            questions = await self._call_llm(prompt)

            logger.info(f"[TaskPlanner] 问询问题: {questions}")

            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="success",
                data={
                    "questions": questions,
                    "requirements": {}
                },
                message="已生成问询问题"
            )

        # 已有初始需求，进行整理和分析
        prompt = f"""根据以下用户提供的信息，整理县志编纂需求：

{initial_requirements}

请整理出以下内容：
1. 县级行政区
2. 编纂目的
3. 时间范围
4. 编纂类型
5. 特殊要求

以JSON格式返回。"""

        requirements_text = await self._call_llm(prompt)

        logger.info(f"[TaskPlanner] 需求整理: {requirements_text}")

        # 简化处理：使用用户输入的需求
        requirements = {
            "county": initial_requirements.get("county", ""),
            "purpose": initial_requirements.get("purpose", ""),
            "time_range": initial_requirements.get("time_range", ""),
            "type": initial_requirements.get("type", ""),
            "special_requirements": initial_requirements.get("special_requirements", ""),
            "confirmed": True
        }

        return AgentResult(
            task_id=task.task_id,
            agent_type=self.agent_type,
            status="success",
            data={
                "requirements": requirements
            },
            message="需求确认完成",
            metadata={"raw_requirements": requirements_text}
        )

    async def _generate_catalog(self, task: AgentTask) -> AgentResult:
        """
        目录生成

        Args:
            task: Agent任务

        Returns:
            执行结果
        """
        logger.info("[TaskPlanner] 开始生成目录")

        user_requirements = task.params.get("user_requirements", {})

        # 构建目录生成提示词
        prompt = f"""请根据以下县志编纂需求，生成符合国标规范的县志目录结构：

县级行政区：{user_requirements.get('county', '')}
编纂目的：{user_requirements.get('purpose', '')}
时间范围：{user_requirements.get('time_range', '')}
编纂类型：{user_requirements.get('type', '')}

请生成完整的目录结构，包括：
- 卷
- 篇
- 章

目录结构应符合《地方志书质量规定》的要求。

以JSON数组格式返回，每个元素包含：
- chapter_id: 章节ID（格式：ch01, ch02, ...）
- title: 章节标题
- level: 层级（1=卷，2=篇，3=章）
- parent_id: 父章节ID（可选）
- order: 排序号

示例格式：
[
  {{"chapter_id": "ch01", "title": "概述", "level": 1, "order": 1}},
  {{"chapter_id": "ch01_01", "title": "建置区划", "level": 2, "parent_id": "ch01", "order": 1}},
  ...
]"""

        catalog_text = await self._call_llm(prompt)

        logger.info(f"[TaskPlanner] 生成的目录: {catalog_text[:500]}...")

        # 简化处理：生成默认目录结构
        # 实际应用中需要解析LLM返回的JSON

        default_catalog = [
            {"chapter_id": "ch01", "title": "概述", "level": 1, "order": 1},
            {"chapter_id": "ch02", "title": "建置区划", "level": 1, "order": 2},
            {"chapter_id": "ch03", "title": "自然环境", "level": 1, "order": 3},
            {"chapter_id": "ch04", "title": "人口", "level": 1, "order": 4},
            {"chapter_id": "ch05", "title": "经济", "level": 1, "order": 5},
            {"chapter_id": "ch06", "title": "政治", "level": 1, "order": 6},
            {"chapter_id": "ch07", "title": "文化", "level": 1, "order": 7},
            {"chapter_id": "ch08", "title": "社会", "level": 1, "order": 8},
            {"chapter_id": "ch09", "title": "人物", "level": 1, "order": 9},
            {"chapter_id": "ch10", "title": "大事记", "level": 1, "order": 10},
        ]

        return AgentResult(
            task_id=task.task_id,
            agent_type=self.agent_type,
            status="success",
            data={
                "catalog": default_catalog
            },
            message=f"目录生成完成，共{len(default_catalog)}章",
            metadata={"raw_catalog": catalog_text}
        )

    async def _assign_tasks(self, task: AgentTask) -> AgentResult:
        """
        任务分配

        Args:
            task: Agent任务

        Returns:
            执行结果
        """
        logger.info("[TaskPlanner] 开始分配任务")

        catalog = task.params.get("catalog", [])
        members = task.params.get("members", [])

        # 构建任务分配提示词
        member_info = "\n".join([
            f"- {m.get('name', '')}: {m.get('role', '')}, 专业领域: {', '.join(m.get('expertise', []))}"
            for m in members
        ])

        chapter_info = "\n".join([
            f"- {ch.get('chapter_id', '')}: {ch.get('title', '')}"
            for ch in catalog
        ])

        prompt = f"""请根据以下信息，合理分配县志编纂任务：

成员信息：
{member_info}

章节信息：
{chapter_info}

任务分配原则：
1. 每个章节需要分配1-2名撰稿人
2. 每个章节需要分配1-2名审核人
3. 撰稿人和审核人不应是同一人
4. 考虑成员的专业领域匹配度
5. 均衡分配工作负载

以JSON对象格式返回，键为章节ID，值为：
- drafters: 撰稿人ID列表
- reviewers: 审核人ID列表

示例格式：
{{
  "ch01": {{"drafters": ["user001"], "reviewers": ["user002"]}},
  "ch02": {{"drafters": ["user002"], "reviewers": ["user001"]}},
  ...
}}"""

        assignment_text = await self._call_llm(prompt)

        logger.info(f"[TaskPlanner] 任务分配: {assignment_text[:500]}...")

        # 简化处理：平均分配任务
        if not members:
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="success",
                data={"assignments": {}},
                message="无成员，无需分配任务"
            )

        assignments = {}
        member_ids = [m.get("member_id", "") for m in members]
        num_members = len(member_ids)

        for i, chapter in enumerate(catalog):
            chapter_id = chapter.get("chapter_id", "")

            # 简单循环分配
            drafter_idx = i % num_members
            reviewer_idx = (i + 1) % num_members

            assignments[chapter_id] = {
                "drafters": [member_ids[drafter_idx]],
                "reviewers": [member_ids[reviewer_idx]]
            }

        logger.info(f"[TaskPlanner] 任务分配完成，共{len(assignments)}个章节")

        return AgentResult(
            task_id=task.task_id,
            agent_type=self.agent_type,
            status="success",
            data={
                "assignments": assignments
            },
            message=f"任务分配完成，共{len(assignments)}个章节",
            metadata={"raw_assignment": assignment_text}
        )

    # ========== ReAct方法实现 ==========

    async def _think(self, task: AgentTask, iteration: int) -> str:
        """推理过程"""
        # 根据任务类型生成思考内容
        action = task.action

        if action == "inquire_requirements":
            if iteration == 1:
                return "我需要向用户询问县志编纂的基本信息，包括县名、编纂目的、时间范围等。"
            else:
                return "需求问询已完成，可以结束。"

        elif action == "generate_catalog":
            if iteration == 1:
                return f"我需要根据用户需求 '{task.params.get('user_requirements')}' 生成县志目录结构。"
            else:
                return "目录生成已完成，可以结束。"

        elif action == "assign_tasks":
            if iteration == 1:
                return f"我需要为 {len(task.params.get('catalog', []))} 个章节分配撰稿和审核任务。"
            else:
                return "任务分配已完成，可以结束。"

        return "任务完成，结束"

    async def _act(self, thought: str, task: AgentTask) -> tuple:
        """执行行动"""
        # TaskPlannerAgent不需要调用外部工具，直接在_think中完成思考
        # 这里返回空，由_finalize处理具体执行
        return None, None

    async def _observe(self, action: str, action_input: Dict[str, Any], task: AgentTask) -> str:
        """观察执行结果"""
        # TaskPlannerAgent的实际执行在各个独立方法中
        return "任务执行完成"

    async def _finalize(self, task: AgentTask) -> AgentResult:
        """生成最终结果"""
        # 调用具体执行方法
        action = task.action

        if action == "inquire_requirements":
            return await self._inquire_requirements(task)
        elif action == "generate_catalog":
            return await self._generate_catalog(task)
        elif action == "assign_tasks":
            return await self._assign_tasks(task)
        else:
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="failure",
                data={},
                message=f"未知操作: {action}",
                errors=[f"Unknown action: {action}"]
            )
