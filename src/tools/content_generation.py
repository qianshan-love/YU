"""
内容生成工具
基于大模型生成县志内容
"""
from typing import Dict, Any, List, Optional
import logging

from src.tools.llm_service import get_llm_service, call_llm
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ContentGenerationTool:
    """内容生成工具"""

    def __init__(self):
        """初始化内容生成工具"""
        self.llm_service = get_llm_service()
        logger.info("内容生成工具初始化完成")

    async def generate_chapter_content(
        self,
        chapter_type: str,
        chapter_title: str,
        knowledge_context: str = "",
        specification: str = "",
        style_guide: str = ""
    ) -> Dict[str, Any]:
        """
        生成章节内容

        Args:
            chapter_type: 章节类型（概述、历史、地理等）
            chapter_title: 章节标题
            knowledge_context: 知识上下文
            specification: 撰写规范
            style_guide: 文风指导

        Returns:
            生成结果
        """
        try:
            # 构建系统提示词
            system_prompt = f"""你是县志编纂专家，擅长撰写符合《地方志书质量规定》的县志内容。

撰写原则：
1. 坚持实事求是，确保史料真实可靠
2. 内容系统完整，涵盖该章节应包含的所有方面
3. 文风庄重典雅，符合县志文风规范
4. 数据准确，时间、地点、人物、事件等要素准确无误
5. 结构清晰，层次分明，逻辑严谨

{specification}

{style_guide}
"""

            # 构建用户提示词
            user_prompt = f"""请撰写《县志》中"{chapter_title}"这一章的内容。

章节类型：{chapter_type}
章节标题：{chapter_title}

{knowledge_context}

请按照县志规范撰写，确保内容真实、准确、系统、完整。"""

            logger.info(f"生成章节内容: {chapter_title} ({chapter_type})")

            # 调用大模型
            result = await self.llm_service.generate_text(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2048
            )

            if result["success"]:
                logger.info(f"章节内容生成成功，长度: {len(result['content'])}")
                return {
                    "success": True,
                    "content": result["content"],
                    "chapter_type": chapter_type,
                    "chapter_title": chapter_title,
                    "usage": result.get("usage", {}),
                    "word_count": len(result["content"])
                }
            else:
                logger.error(f"章节内容生成失败: {result.get('error')}")
                return {
                    "success": False,
                    "error": result.get("error"),
                    "message": result.get("message", "生成失败")
                }

        except Exception as e:
            logger.error(f"内容生成异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "生成异常"
            }

    async def generate_section(
        self,
        section_title: str,
        context: str,
        length_requirement: str = "适中"
    ) -> Dict[str, Any]:
        """
        生成小节内容

        Args:
            section_title: 小节标题
            context: 上下文信息
            length_requirement: 长度要求（简短/适中/详细）

        Returns:
            生成结果
        """
        try:
            system_prompt = """你是县志编纂专家，擅长撰写符合规范的县志小节内容。

撰写要求：
- 内容简明扼要，重点突出
- 数据准确，有据可查
- 文风规范，用词准确
- 逻辑清晰，层次分明
"""

            length_map = {
                "简短": "约200-300字",
                "适中": "约500-800字",
                "详细": "约1000-1500字"
            }

            user_prompt = f"""请撰写县志中的"{section_title}"这一小节的内容。

上下文信息：
{context}

长度要求：{length_map.get(length_requirement, "适中")}

请确保内容准确、规范。"""

            logger.info(f"生成小节内容: {section_title}")

            result = await self.llm_service.generate_text(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.6,
                max_tokens=1024
            )

            if result["success"]:
                logger.info(f"小节内容生成成功，长度: {len(result['content'])}")
                return {
                    "success": True,
                    "content": result["content"],
                    "section_title": section_title,
                    "usage": result.get("usage", {}),
                    "word_count": len(result["content"])
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error"),
                    "message": result.get("message", "生成失败")
                }

        except Exception as e:
            logger.error(f"小节生成异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "生成异常"
            }

    async def generate_catalog(
        self,
        requirements: Dict[str, Any],
        county_name: str = "示例县"
    ) -> Dict[str, Any]:
        """
        生成县志目录

        Args:
            requirements: 编纂需求
            county_name: 县名

        Returns:
            目录生成结果
        """
        try:
            system_prompt = """你是县志编纂专家，熟悉《地方志书质量规定》和县志体例规范。

目录生成原则：
- 符合国标GB/T 2266-2019《地方志书质量规定》
- 结构完整，涵盖县志应有的主要组成部分
- 层次清晰，卷、篇、章、节、目层次分明
- 逻辑合理，各章节之间衔接自然
"""

            user_prompt = f"""请为《{county_name}志》生成完整的目录结构。

编纂需求：
{requirements}

请按照国标规范生成县志目录，包括卷、篇、章、节、目等层级结构。
目录应涵盖：概述、历史沿革、地理环境、行政区划、人口民族、经济、政治、文化、社会、人物、大事记等主要部分。"""

            logger.info(f"生成县志目录: {county_name}")

            result = await self.llm_service.generate_text(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=1536
            )

            if result["success"]:
                logger.info(f"目录生成成功，长度: {len(result['content'])}")
                return {
                    "success": True,
                    "catalog": result["content"],
                    "county_name": county_name,
                    "usage": result.get("usage", {}),
                    "word_count": len(result["content"])
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error"),
                    "message": result.get("message", "生成失败")
                }

        except Exception as e:
            logger.error(f"目录生成异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "生成异常"
            }

    async def improve_content(
        self,
        original_content: str,
        feedback: str,
        improvement_type: str = "general"
    ) -> Dict[str, Any]:
        """
        改进内容

        Args:
            original_content: 原始内容
            feedback: 改进建议
            improvement_type: 改进类型（general/grammar/fact/structure）

        Returns:
            改进结果
        """
        try:
            improvement_prompts = {
                "general": "请对内容进行整体改进，提升质量和规范性。",
                "grammar": "请修正内容中的语法错误和用词不当之处。",
                "fact": "请核验并修正内容中的事实错误。",
                "structure": "请优化内容的结构和逻辑，使其更加清晰连贯。"
            }

            system_prompt = """你是县志编纂专家，擅长改进和完善县志内容。

改进原则：
- 保持原文的真实性和准确性
- 修正错误，优化表达
- 提升内容质量和规范性
- 符合县志文风规范
"""

            user_prompt = f"""请改进以下县志内容：

原始内容：
{original_content}

改进建议：
{feedback}

改进类型：{improvement_type}
具体要求：{improvement_prompts.get(improvement_type, improvement_prompts["general"])}

请提供改进后的内容。"""

            logger.info(f"改进内容，类型: {improvement_type}")

            result = await self.llm_service.generate_text(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=2048
            )

            if result["success"]:
                logger.info(f"内容改进成功")
                return {
                    "success": True,
                    "improved_content": result["content"],
                    "original_content": original_content,
                    "feedback": feedback,
                    "improvement_type": improvement_type,
                    "usage": result.get("usage", {}),
                    "word_count": len(result["content"])
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error"),
                    "message": result.get("message", "改进失败")
                }

        except Exception as e:
            logger.error(f"内容改进异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "改进异常"
            }


# 全局内容生成工具实例
_content_generation_tool: Optional[ContentGenerationTool] = None


def get_content_generation_tool() -> ContentGenerationTool:
    """获取内容生成工具单例"""
    global _content_generation_tool
    if _content_generation_tool is None:
        _content_generation_tool = ContentGenerationTool()
    return _content_generation_tool


# 便捷函数
async def generate_chapter(
    chapter_type: str,
    chapter_title: str,
    knowledge_context: str = "",
    specification: str = ""
) -> str:
    """便捷的章节生成函数"""
    tool = get_content_generation_tool()
    result = await tool.generate_chapter_content(
        chapter_type=chapter_type,
        chapter_title=chapter_title,
        knowledge_context=knowledge_context,
        specification=specification
    )

    if result["success"]:
        return result["content"]
    else:
        logger.error(f"章节生成失败: {result.get('error')}")
        return ""
