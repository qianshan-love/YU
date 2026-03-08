"""
规范查询工具
用于查询《地方志书质量规定》、县志术语、行文规范
"""
from typing import Dict, Any, List, Optional
import logging
import json
from pathlib import Path

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class SpecificationTool:
    """规范查询工具"""

    def __init__(self):
        """初始化规范查询工具"""
        self.specifications = self._load_specifications()
        self.terminologies = self._load_terminologies()
        self.writing_styles = self._load_writing_styles()

        logger.info("规范查询工具初始化完成")

    def _load_specifications(self) -> Dict[str, Any]:
        """
        加载规范库

        Returns:
            规范字典
        """
        # 模拟规范库数据
        # 实际应用中应从数据库或文件加载

        return {
            "地方志书质量规定": {
                "version": "2017",
                "principles": [
                    "实事求是，存真求实",
                    "述而不论，寓论于述",
                    "横排门类，纵述史实",
                    "语言规范，文字精炼",
                    "资料翔实，数据准确"
                ],
                "requirements": {
                    "content": {
                        "政治性": "坚持正确政治方向",
                        "史料性": "史料真实可靠",
                        "系统性": "内容系统完整",
                        "准确性": "数据准确无误"
                    },
                    "structure": {
                        "篇目设置": "科学合理，层次清晰",
                        "章节安排": "逻辑严密，衔接自然",
                        "篇幅控制": "详略得当，主次分明"
                    },
                    "language": {
                        "文体": "采用志体文体",
                        "用语": "规范、准确、简洁",
                        "表述": "客观、中立、公正"
                    }
                }
            },
            "章节撰写规范": {
                "概述": {
                    "定位": "概述全志主要内容",
                    "要求": "提纲挈领，简明扼要",
                    "字数": "2000-3000字"
                },
                "建置区划": {
                    "定位": "记述建置沿革和行政区划变化",
                    "要求": "时间清晰，沿革准确",
                    "字数": "3000-5000字"
                },
                "自然环境": {
                    "定位": "记述地理环境和自然资源",
                    "要求": "数据准确，描述客观",
                    "字数": "4000-6000字"
                },
                "人口": {
                    "定位": "记述人口数量、结构、分布",
                    "要求": "统计准确，分析合理",
                    "字数": "3000-4000字"
                },
                "经济": {
                    "定位": "记述经济发展状况和成就",
                    "要求": "数据真实，分析客观",
                    "字数": "6000-8000字"
                },
                "政治": {
                    "定位": "记述政治体制改革和政权建设",
                    "要求": "表述准确，评价中肯",
                    "字数": "5000-7000字"
                },
                "文化": {
                    "定位": "记述文化事业发展情况",
                    "要求": "内容丰富，特色鲜明",
                    "字数": "4000-6000字"
                },
                "社会": {
                    "定位": "记述社会事业发展和民生改善",
                    "要求": "贴近实际，突出实效",
                    "字数": "4000-6000字"
                },
                "人物": {
                    "定位": "记述重要人物事迹",
                    "要求": "坚持标准，记述客观",
                    "字数": "3000-5000字"
                },
                "大事记": {
                    "定位": "按时间顺序记述大事要事",
                    "要求": "选材准确，记述简明",
                    "字数": "3000-5000字"
                }
            }
        }

    def _load_terminologies(self) -> Dict[str, Any]:
        """
        加载术语库

        Returns:
            术语字典
        """
        return {
            "县志术语": {
                "续修": "在原有志书基础上，继续编纂后续时期的志书",
                "重修": "对原有志书进行全面重新编纂",
                "增修": "在原有志书基础上增补内容",
                "补遗": "补充遗漏的内容",
                "订正": "纠正错误的内容",
                "志体": "地方志的文体形式，以记叙为主，寓论于述",
                "横排纵述": "横排门类，纵述史实，先分类后按时间顺序记述",
                "述而不论": "只记述事实，不直接发表议论",
                "生不立传": "健在的人物不立传，可入表",
                "生不列传": "健在的人物不入人物传",
                "以事系人": "通过记述事件来反映人物事迹",
                "越境不书": "不记述本县以外的事情",
                "详今略古": "详写现代，略写古代"
            },
            "数据术语": {
                "统计年度": "统计数据的所属年份",
                "统计口径": "统计数据的范围和方法",
                "数据来源": "数据的出处和提供单位",
                "增长率": "增长量与基期量之比",
                "比重": "部分占总体的比例",
                "人均": "平均每人拥有的数量"
            }
        }

    def _load_writing_styles(self) -> Dict[str, Any]:
        """
        加载文风规范

        Returns:
            文风字典
        """
        return {
            "语言要求": {
                "准确性": {
                    "用词": "用词准确，概念清晰",
                    "数据": "数据准确，有据可查",
                    "表述": "表述准确，不产生歧义"
                },
                "简洁性": {
                    "文字": "文字精炼，避免冗余",
                    "结构": "结构清晰，层次分明",
                    "篇幅": "篇幅适当，详略得当"
                },
                "客观性": {
                    "立场": "立场客观，不偏不倚",
                    "评价": "评价中肯，实事求是",
                    "叙述": "叙述平实，不夸张渲染"
                },
                "规范性": {
                    "格式": "格式规范，统一标准",
                    "标点": "标点正确，使用规范",
                    "数字": "数字用法符合规范"
                }
            },
            "禁止用语": {
                "主观表达": ["我认为", "我们觉得", "在作者看来"],
                "不确定表达": ["可能", "大概", "或许", "估计"],
                "情绪化表达": ["激动人心", "令人振奋", "无比自豪"],
                "夸张表达": ["史无前例", "空前绝后", "前所未有"]
            },
            "推荐用语": {
                "时间表达": ["2020年", "2020-2025年", "二十世纪八十年代"],
                "数量表达": ["约5000人", "超过1亿元", "约占30%"],
                "程度表达": ["显著提高", "大幅增长", "稳步发展"]
            }
        }

    async def query_specification(
        self,
        spec_type: str,
        spec_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        查询规范

        Args:
            spec_type: 规范类型（地方志书质量规定/章节撰写规范）
            spec_key: 规范键（可选，用于查询具体章节）

        Returns:
            规范内容
        """
        logger.info(f"查询规范: {spec_type} -> {spec_key}")

        try:
            # 查询规范
            spec = self.specifications.get(spec_type)

            if spec is None:
                logger.warning(f"规范不存在: {spec_type}")
                return {
                    "success": False,
                    "message": f"规范不存在: {spec_type}",
                    "data": {}
                }

            # 如果指定了键，返回具体内容
            if spec_key:
                if spec_key in spec:
                    return {
                        "success": True,
                        "message": "查询成功",
                        "data": spec[spec_key]
                    }
                else:
                    return {
                        "success": False,
                        "message": f"规范键不存在: {spec_key}",
                        "data": {}
                    }

            # 返回全部规范
            return {
                "success": True,
                "message": "查询成功",
                "data": spec
            }

        except Exception as e:
            logger.error(f"查询规范异常: {str(e)}")
            return {
                "success": False,
                "message": f"查询异常: {str(e)}",
                "data": {}
            }

    async def query_terminology(
        self,
        term: str,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        查询术语

        Args:
            term: 术语
            category: 类别（可选）

        Returns:
            术语解释
        """
        logger.info(f"查询术语: {term}")

        try:
            # 遍历术语库查找
            for category_name, terms in self.terminologies.items():
                if category and category != category_name:
                    continue

                if term in terms:
                    return {
                        "success": True,
                        "message": "查询成功",
                        "data": {
                            "term": term,
                            "definition": terms[term],
                            "category": category_name
                        }
                    }

            # 未找到术语
            return {
                "success": False,
                "message": f"术语不存在: {term}",
                "data": {}
            }

        except Exception as e:
            logger.error(f"查询术语异常: {str(e)}")
            return {
                "success": False,
                "message": f"查询异常: {str(e)}",
                "data": {}
            }

    async def query_writing_style(
        self,
        style_type: Optional[str] = None,
        style_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        查询文风规范

        Args:
            style_type: 文风类型（语言要求/禁止用语/推荐用语）
            style_key: 文风键（可选）

        Returns:
            文风规范内容
        """
        logger.info(f"查询文风规范: {style_type} -> {style_key}")

        try:
            # 查询文风规范
            styles = self.writing_styles

            if style_type:
                if style_type not in styles:
                    return {
                        "success": False,
                        "message": f"文风类型不存在: {style_type}",
                        "data": {}
                    }

                style_content = styles[style_type]

                if style_key:
                    if style_key in style_content:
                        return {
                            "success": True,
                            "message": "查询成功",
                            "data": style_content[style_key]
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"文风键不存在: {style_key}",
                            "data": {}
                        }

                return {
                    "success": True,
                    "message": "查询成功",
                    "data": style_content
                }

            # 返回全部文风规范
            return {
                "success": True,
                "message": "查询成功",
                "data": styles
            }

        except Exception as e:
            logger.error(f"查询文风规范异常: {str(e)}")
            return {
                "success": False,
                "message": f"查询异常: {str(e)}",
                "data": {}
            }

    async def get_chapter_specification(
        self,
        chapter_type: str
    ) -> Dict[str, Any]:
        """
        获取章节撰写规范

        Args:
            chapter_type: 章节类型（概述/建置区划/自然环境/人口/经济/政治/文化/社会/人物/大事记）

        Returns:
            章节规范
        """
        logger.info(f"获取章节撰写规范: {chapter_type}")

        # 规范类型映射
        chapter_map = {
            "概述": "概述",
            "建置区划": "建置区划",
            "自然环境": "自然环境",
            "人口": "人口",
            "经济": "经济",
            "政治": "政治",
            "文化": "文化",
            "社会": "社会",
            "人物": "人物",
            "大事记": "大事记"
        }

        spec_key = chapter_map.get(chapter_type, chapter_type)

        result = await self.query_specification("章节撰写规范", spec_key)

        if result["success"]:
            return {
                "success": True,
                "message": "获取成功",
                "data": {
                    "chapter_type": chapter_type,
                    **result["data"]
                }
            }
        else:
            # 返回通用规范
            return {
                "success": True,
                "message": "获取通用规范",
                "data": {
                    "chapter_type": chapter_type,
                    "定位": "根据目录定位章节内容",
                    "要求": "内容真实、数据准确、语言规范",
                    "字数": "3000-5000字"
                }
            }

    async def validate_content(
        self,
        content: str,
        validation_rules: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        校验内容规范

        Args:
            content: 内容
            validation_rules: 校验规则列表

        Returns:
            校验结果
        """
        logger.info(f"校验内容规范，内容长度: {len(content)}")

        errors = []
        warnings = []

        # 默认校验规则
        if validation_rules is None:
            validation_rules = [
                "check_forbidden_words",
                "check_uncertain_expressions",
                "check_data_sources",
                "check_structure"
            ]

        # 执行校验
        if "check_forbidden_words" in validation_rules:
            forbidden_result = await self._check_forbidden_words(content)
            if forbidden_result["errors"]:
                errors.extend(forbidden_result["errors"])

        if "check_uncertain_expressions" in validation_rules:
            uncertain_result = await self._check_uncertain_expressions(content)
            if uncertain_result["errors"]:
                warnings.extend(uncertain_result["errors"])

        if "check_data_sources" in validation_rules:
            source_result = await self._check_data_sources(content)
            if source_result["warnings"]:
                warnings.extend(source_result["warnings"])

        if "check_structure" in validation_rules:
            structure_result = await self._check_structure(content)
            if structure_result["errors"]:
                errors.extend(structure_result["errors"])

        # 判断校验结果
        passed = len(errors) == 0

        return {
            "success": True,
            "message": "校验完成",
            "data": {
                "passed": passed,
                "errors": errors,
                "warnings": warnings,
                "error_count": len(errors),
                "warning_count": len(warnings)
            }
        }

    async def _check_forbidden_words(self, content: str) -> Dict[str, List[str]]:
        """检查禁止用语"""
        errors = []

        forbidden_words = self.writing_styles.get("禁止用语", {})
        for category, words in forbidden_words.items():
            for word in words:
                if word in content:
                    errors.append(f"包含禁止用语（{category}）：'{word}'")

        return {"errors": errors}

    async def _check_uncertain_expressions(self, content: str) -> Dict[str, List[str]]:
        """检查不确定表达"""
        warnings = []

        uncertain_expressions = self.writing_styles.get("禁止用语", {}).get("不确定表达", [])
        for expr in uncertain_expressions:
            if expr in content:
                warnings.append(f"包含不确定表达：'{expr}'，建议修改")

        return {"warnings": warnings}

    async def _check_data_sources(self, content: str) -> Dict[str, List[str]]:
        """检查数据来源"""
        warnings = []

        # 检查是否包含数据但未注明来源
        if "数据" in content and "来源" not in content:
            warnings.append("包含数据引用但未注明来源，请补充数据来源")

        # 检查是否包含百分比
        if "%" in content and "来源" not in content:
            warnings.append("包含百分比数据，建议注明来源")

        return {"warnings": warnings}

    async def _check_structure(self, content: str) -> Dict[str, List[str]]:
        """检查结构"""
        errors = []

        # 检查是否有段落
        paragraphs = content.split('\n')
        if len(paragraphs) < 2:
            errors.append("文章结构过于简单，建议增加段落")

        # 检查是否有结构标记
        if not any(marker in content for marker in ["一、", "（一）", "1.", "第一", "首先"]):
            errors.append("文章结构不够清晰，建议使用数字序号组织内容")

        return {"errors": errors}


# 全局规范查询工具实例
_specification_tool: Optional[SpecificationTool] = None


def get_specification_tool() -> SpecificationTool:
    """获取规范查询工具单例"""
    global _specification_tool
    if _specification_tool is None:
        _specification_tool = SpecificationTool()
    return _specification_tool
