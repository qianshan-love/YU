"""
知识规范 Agent
负责规范查询、知识检索、规范校验
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from src.agents.base_agent import BaseAgent
from src.models.agent import AgentTask, AgentResult
from src.tools.specification import get_specification_tool
from src.tools.retrieval import get_retrieval_tool
from src.tools.web_search import get_web_search_tool
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class KnowledgeAgent(BaseAgent):
    """知识规范Agent"""

    def __init__(self, agent_config: Dict[str, Any]):
        """初始化知识规范Agent"""
        super().__init__(agent_config)

        # 初始化工具
        self.specification_tool = get_specification_tool()
        self.retrieval_tool = get_retrieval_tool()
        self.web_search_tool = get_web_search_tool()

        logger.info("知识规范Agent初始化完成")

    def get_agent_type(self) -> str:
        return "knowledge"

    def _initialize_tools(self) -> List[Any]:
        """初始化工具集"""
        # 知识规范Agent不需要额外的工具类，直接调用工具函数
        return []

    def get_system_prompt(self) -> str:
        return """你是县志知识规范专家。你的职责是：
1. 规范查询：查询《地方志书质量规定》、县志术语、行文规范
2. 知识检索：从规范库、旧志、年鉴中检索相关资料
3. 互联网检索：从互联网检索所需资料
4. 规范校验：校验内容的规范性

你会遵循以下原则：
- 确保规范查询的准确性和完整性
- 检索结果要相关、准确、有据可查
- 互联网检索要过滤无效信息，提取有价值内容
- 规范校验要严格、细致、全面

可用操作：
- query_specification: 查询规范
- retrieve_knowledge: 检索知识
- web_search: 网络搜索
- validate_content: 校验内容
"""

    def get_agent_schema(self) -> Dict[str, Any]:
        return {
            "agent_type": "knowledge",
            "agent_name": "知识规范Agent",
            "description": "负责规范查询、知识检索、互联网检索、规范校验",
            "actions": [
                "query_specification",
                "retrieve_knowledge",
                "web_search",
                "validate_content"
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

        logger.info(f"[Knowledge] 执行任务: {action}")

        try:
            if action == "query_specification":
                return await self._query_specification(task)
            elif action == "retrieve_knowledge":
                return await self._retrieve_knowledge(task)
            elif action == "web_search":
                return await self._web_search(task)
            elif action == "validate_content":
                return await self._validate_content(task)
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
            logger.error(f"[Knowledge] 执行异常: {str(e)}")
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="failure",
                data={},
                message=f"执行异常: {str(e)}",
                errors=[str(e)]
            )

    async def _query_specification(self, task: AgentTask) -> AgentResult:
        """
        查询规范

        Args:
            task: Agent任务

        Returns:
            执行结果
        """
        logger.info("[Knowledge] 查询规范")

        spec_type = task.params.get("spec_type", "")
        spec_key = task.params.get("spec_key")

        # 章节撰写规范特殊处理
        if spec_type == "chapter_specification":
            chapter_type = task.params.get("chapter_type", "")
            result = await self.specification_tool.get_chapter_specification(chapter_type)
        else:
            result = await self.specification_tool.query_specification(spec_type, spec_key)

        if result["success"]:
            logger.info(f"[Knowledge] 规范查询成功: {spec_type}")
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="success",
                data=result["data"],
                message=result["message"],
                metadata={"spec_type": spec_type, "spec_key": spec_key}
            )
        else:
            logger.warning(f"[Knowledge] 规范查询失败: {result['message']}")
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="partial",
                data={},
                message=result["message"],
                errors=[result["message"]]
            )

    async def _retrieve_knowledge(self, task: AgentTask) -> AgentResult:
        """
        检索知识

        Args:
            task: Agent任务

        Returns:
            执行结果
        """
        logger.info("[Knowledge] 检索知识")

        query = task.params.get("query", "")
        source = task.params.get("source")  # knowledge_base/old_annals/yearbook/comprehensive
        category = task.params.get("category")
        year = task.params.get("year")
        limit = task.params.get("limit", 5)

        if not query:
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="failure",
                data={},
                message="查询关键词不能为空",
                errors=["查询关键词不能为空"]
            )

        try:
            # 根据来源类型调用不同的检索方法
            if source == "knowledge_base":
                result = await self.retrieval_tool.search_knowledge_base(query, category, limit)

            elif source == "old_annals":
                result = await self.retrieval_tool.search_old_annals(query, limit)

            elif source == "yearbook":
                result = await self.retrieval_tool.search_yearbook(query, year, limit)

            elif source == "comprehensive":
                sources = task.params.get("sources", ["knowledge_base", "old_annals", "yearbook"])
                result = await self.retrieval_tool.comprehensive_search(query, sources, limit)

            else:
                # 默认综合搜索
                result = await self.retrieval_tool.comprehensive_search(query, None, limit)

            if result["success"]:
                logger.info(f"[Knowledge] 知识检索成功: {query}, 找到{result['data']['total']}条结果")

                # 如果结果为空，尝试网络搜索
                if result["data"]["total"] == 0:
                    logger.info(f"[Knowledge] 知识库无结果，尝试网络搜索")
                    web_result = await self.web_search_tool.search(query, limit)

                    if web_result["success"]:
                        logger.info(f"[Knowledge] 网络搜索成功，找到{web_result['data']['total']}条结果")

                        # 合并结果
                        result["data"]["results"].extend(web_result["data"]["results"])
                        result["data"]["total"] += web_result["data"]["total"]
                        result["message"] += f"，网络搜索补充{web_result['data']['total']}条"

                return AgentResult(
                    task_id=task.task_id,
                    agent_type=self.agent_type,
                    status="success",
                    data=result["data"],
                    message=result["message"],
                    metadata={"query": query, "source": source}
                )
            else:
                logger.warning(f"[Knowledge] 知识检索失败: {result['message']}")
                return AgentResult(
                    task_id=task.task_id,
                    agent_type=self.agent_type,
                    status="failure",
                    data={},
                    message=result["message"],
                    errors=[result["message"]]
                )

        except Exception as e:
            logger.error(f"[Knowledge] 知识检索异常: {str(e)}")
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="failure",
                data={},
                message=f"检索异常: {str(e)}",
                errors=[str(e)]
            )

    async def _web_search(self, task: AgentTask) -> AgentResult:
        """
        网络搜索

        Args:
            task: Agent任务

        Returns:
            执行结果
        """
        logger.info("[Knowledge] 网络搜索")

        query = task.params.get("query", "")
        num_results = task.params.get("num_results", 5)
        source = task.params.get("source", "mock")

        if not query:
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="failure",
                data={},
                message="搜索关键词不能为空",
                errors=["搜索关键词不能为空"]
            )

        try:
            result = await self.web_search_tool.search(query, num_results, source)

            if result["success"]:
                logger.info(f"[Knowledge] 网络搜索成功: {query}, 找到{result['data']['total']}条结果")
                return AgentResult(
                    task_id=task.task_id,
                    agent_type=self.agent_type,
                    status="success",
                    data=result["data"],
                    message=result["message"],
                    metadata={"query": query, "source": source}
                )
            else:
                logger.warning(f"[Knowledge] 网络搜索失败: {result['message']}")
                return AgentResult(
                    task_id=task.task_id,
                    agent_type=self.agent_type,
                    status="failure",
                    data={},
                    message=result["message"],
                    errors=[result["message"]]
                )

        except Exception as e:
            logger.error(f"[Knowledge] 网络搜索异常: {str(e)}")
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="failure",
                data={},
                message=f"搜索异常: {str(e)}",
                errors=[str(e)]
            )

    async def _validate_content(self, task: AgentTask) -> AgentResult:
        """
        校验内容规范

        Args:
            task: Agent任务

        Returns:
            执行结果
        """
        logger.info("[Knowledge] 校验内容规范")

        content = task.params.get("content", "")
        validation_rules = task.params.get("validation_rules")

        if not content:
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="failure",
                data={},
                message="内容不能为空",
                errors=["内容不能为空"]
            )

        try:
            result = await self.specification_tool.validate_content(content, validation_rules)

            if result["success"]:
                passed = result["data"]["passed"]
                error_count = result["data"]["error_count"]
                warning_count = result["data"]["warning_count"]

                logger.info(f"[Knowledge] 内容校验完成，通过: {passed}, 错误: {error_count}, 警告: {warning_count}")

                return AgentResult(
                    task_id=task.task_id,
                    agent_type=self.agent_type,
                    status="success",
                    data=result["data"],
                    message=f"校验完成，{'通过' if passed else f'有{error_count}个错误'}",
                    metadata={
                        "passed": passed,
                        "error_count": error_count,
                        "warning_count": warning_count
                    }
                )
            else:
                logger.warning(f"[Knowledge] 内容校验失败: {result['message']}")
                return AgentResult(
                    task_id=task.task_id,
                    agent_type=self.agent_type,
                    status="failure",
                    data={},
                    message=result["message"],
                    errors=[result["message"]]
                )

        except Exception as e:
            logger.error(f"[Knowledge] 内容校验异常: {str(e)}")
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="failure",
                data={},
                message=f"校验异常: {str(e)}",
                errors=[str(e)]
            )

    # ========== ReAct方法实现 ==========

    async def _think(self, task: AgentTask, iteration: int) -> str:
        """推理过程"""
        action = task.action
        params = task.params

        if action == "query_specification":
            spec_type = params.get("spec_type", "")
            spec_key = params.get("spec_key")
            if iteration == 1:
                return f"我需要查询规范: {spec_type}，键: {spec_key}"
            elif iteration == 2:
                return f"正在执行规范查询..."
            else:
                return f"规范查询完成。"

        elif action == "retrieve_knowledge":
            query = params.get("query", "")
            source = params.get("source", "comprehensive")
            if iteration == 1:
                return f"我需要检索知识: {query}，数据源: {source}"
            elif iteration == 2:
                return f"正在执行知识检索..."
            else:
                return f"知识检索完成。"

        elif action == "web_search":
            query = params.get("query", "")
            if iteration == 1:
                return f"我需要网络搜索: {query}"
            elif iteration == 2:
                return f"正在执行网络搜索..."
            else:
                return f"网络搜索完成。"

        elif action == "validate_content":
            if iteration == 1:
                return f"我需要校验内容规范，内容长度: {len(params.get('content', ''))}"
            elif iteration == 2:
                return f"正在执行内容校验..."
            else:
                return f"内容校验完成。"

        return "任务完成，结束"

    async def _act(self, thought: str, task: AgentTask) -> tuple:
        """执行行动"""
        # KnowledgeAgent的实际执行在独立方法中
        return None, None

    async def _observe(self, action: str, action_input: Dict[str, Any], task: AgentTask) -> str:
        """观察执行结果"""
        return "任务执行完成"

    async def _finalize(self, task: AgentTask) -> AgentResult:
        """生成最终结果"""
        action = task.action

        if action == "query_specification":
            return await self._query_specification(task)
        elif action == "retrieve_knowledge":
            return await self._retrieve_knowledge(task)
        elif action == "web_search":
            return await self._web_search(task)
        elif action == "validate_content":
            return await self._validate_content(task)
        else:
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                status="failure",
                data={},
                message=f"未知操作: {action}",
                errors=[f"Unknown action: {action}"]
            )
