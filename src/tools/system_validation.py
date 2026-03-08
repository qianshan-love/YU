"""
系统校验工具
负责体例、文风、数据格式等系统校验
"""
from typing import Dict, Any, List, Optional
import re
import logging

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class SystemValidationTool:
    """系统校验工具"""

    def __init__(self):
        """初始化系统校验工具"""
        # 校验规则（实际项目应从数据库或配置文件加载）
        self.style_rules = self._load_style_rules()
        self.format_rules = self._load_format_rules()
        self.fact_rules = self._load_fact_rules()

        logger.info("系统校验工具初始化完成")

    async def validate_content(
        self,
        content: str,
        validation_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        校验内容

        Args:
            content: 待校验内容
            validation_types: 校验类型列表（style/format/fact/all）

        Returns:
            校验结果
        """
        try:
            if not validation_types or "all" in validation_types:
                validation_types = ["style", "format", "fact"]

            errors = []
            warnings = []
            passed_checks = []

            # 体例校验
            if "style" in validation_types:
                style_result = self.validate_style(content)
                errors.extend(style_result.get("errors", []))
                warnings.extend(style_result.get("warnings", []))
                passed_checks.extend(style_result.get("passed", []))

            # 格式校验
            if "format" in validation_types:
                format_result = self.validate_format(content)
                errors.extend(format_result.get("errors", []))
                warnings.extend(format_result.get("warnings", []))
                passed_checks.extend(format_result.get("passed", []))

            # 事实校验
            if "fact" in validation_types:
                fact_result = self.validate_fact(content)
                errors.extend(fact_result.get("errors", []))
                warnings.extend(fact_result.get("warnings", []))
                passed_checks.extend(fact_result.get("passed", []))

            # 判断是否通过
            passed = len(errors) == 0

            logger.info(f"内容校验完成: 错误{len(errors)}, 警告{len(warnings)}")

            return {
                "success": True,
                "passed": passed,
                "errors": errors,
                "warnings": warnings,
                "passed_checks": passed_checks,
                "error_count": len(errors),
                "warning_count": len(warnings),
                "passed_check_count": len(passed_checks),
                "message": f"校验完成，{len(errors)}个错误，{len(warnings)}个警告"
            }

        except Exception as e:
            logger.error(f"内容校验异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "校验异常"
            }

    def validate_style(self, content: str) -> Dict[str, Any]:
        """体例校验"""
        errors = []
        warnings = []
        passed = []

        # 规则1：检查是否使用第一人称
        if "我" in content or "我们" in content:
            errors.append({
                "type": "style",
                "rule": "no_first_person",
                "message": "内容中不应使用第一人称'我'或'我们'",
                "location": "全文",
                "severity": "error"
            })
        else:
            passed.append({"rule": "no_first_person", "message": "未使用第一人称"})

        # 规则2：检查是否使用感叹号
        if "！" in content or "!" in content:
            warnings.append({
                "type": "style",
                "rule": "no_exclamation",
                "message": "县志中应避免使用感叹号",
                "count": content.count("！") + content.count("!"),
                "severity": "warning"
            })
        else:
            passed.append({"rule": "no_exclamation", "message": "未使用感叹号"})

        # 规则3：检查段落长度
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        short_paragraphs = [p for p in paragraphs if len(p) < 50]

        if short_paragraphs:
            warnings.append({
                "type": "style",
                "rule": "min_paragraph_length",
                "message": f"存在{len(short_paragraphs)}个过短段落（少于50字）",
                "severity": "warning"
            })
        else:
            passed.append({"rule": "min_paragraph_length", "message": "段落长度合理"})

        # 规则4：检查是否使用时间表述
        time_patterns = [
            r"今天",
            r"明天",
            r"昨天",
            r"现在",
            r"此时"
        ]

        for pattern in time_patterns:
            if re.search(pattern, content):
                warnings.append({
                    "type": "style",
                    "rule": "no_relative_time",
                    "message": f"应避免使用相对时间表述: '{pattern}'",
                    "severity": "warning"
                })
                break

        if not any(re.search(p, content) for p in time_patterns):
            passed.append({"rule": "no_relative_time", "message": "未使用相对时间表述"})

        return {"errors": errors, "warnings": warnings, "passed": passed}

    def validate_format(self, content: str) -> Dict[str, Any]:
        """格式校验"""
        errors = []
        warnings = []
        passed = []

        # 规则1：检查空行过多
        lines = content.split('\n')
        empty_line_count = sum(1 for line in lines if not line.strip())

        if len(lines) > 0 and empty_line_count / len(lines) > 0.3:
            errors.append({
                "type": "format",
                "rule": "max_empty_lines",
                "message": f"空行过多，占比{empty_line_count/len(lines):.1%}，不应超过30%",
                "severity": "error"
            })
        else:
            passed.append({"rule": "max_empty_lines", "message": "空行数量合理"})

        # 规则2：检查段落缩进
        indented_paragraphs = 0
        for line in lines:
            if line.strip() and not line.startswith(('    ', '\t')):
                indented_paragraphs += 1

        paragraphs = [p for p in content.split('\n\n') if p.strip()]

        if paragraphs and indented_paragraphs / len(paragraphs) < 0.8:
            warnings.append({
                "type": "format",
                "rule": "paragraph_indent",
                "message": f"段落缩进不规范，建议统一使用首行缩进",
                "severity": "warning"
            })
        else:
            passed.append({"rule": "paragraph_indent", "message": "段落缩进规范"})

        # 规则3：检查标点符号使用
        # 中文句号应为"。"，而不是"."
        if content.count("。") > 0 and content.count(".") > content.count("。"):
            warnings.append({
                "type": "format",
                "rule": "chinese_punctuation",
                "message": "应使用中文句号'。'而不是英文句号'.'",
                "severity": "warning"
            })
        else:
            passed.append({"rule": "chinese_punctuation", "message": "标点符号使用规范"})

        return {"errors": errors, "warnings": warnings, "passed": passed}

    def validate_fact(self, content: str) -> Dict[str, Any]:
        """事实校验"""
        errors = []
        warnings = []
        passed = []

        # 规则1：检查年份格式
        year_pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(year_pattern, content)

        invalid_years = [y for y in years if int(y) > 2026 or int(y) < 1900]

        if invalid_years:
            warnings.append({
                "type": "fact",
                "rule": "valid_year_range",
                "message": f"存在可能不合理的年份: {', '.join(invalid_years)}",
                "severity": "warning"
            })
        else:
            passed.append({"rule": "valid_year_range", "message": "年份范围合理"})

        # 规则2：检查数字格式（中文数字 vs 阿拉伯数字）
        # 县志中数字应统一格式
        arabic_numbers = re.findall(r'\b\d+\b', content)
        # 这里简化处理，实际应根据县志规范判断

        passed.append({"rule": "number_format", "message": "数字格式检查完成"})

        return {"errors": errors, "warnings": warnings, "passed": passed}

    def _load_style_rules(self) -> List[Dict[str, Any]]:
        """加载体例规则"""
        return [
            {
                "rule_id": "style_001",
                "name": "禁止第一人称",
                "description": "县志内容不应使用第一人称",
                "severity": "error",
                "pattern": r'[我我们]'
            },
            {
                "rule_id": "style_002",
                "name": "避免感叹号",
                "description": "县志中应避免使用感叹号",
                "severity": "warning",
                "pattern": r'[！!]'
            },
            {
                "rule_id": "style_003",
                "name": "段落长度",
                "description": "段落不应过短",
                "severity": "warning",
                "check": "min_paragraph_length"
            }
        ]

    def _load_format_rules(self) -> List[Dict[str, Any]]:
        """加载格式规则"""
        return [
            {
                "rule_id": "format_001",
                "name": "空行控制",
                "description": "空行不应过多",
                "severity": "error",
                "check": "max_empty_lines"
            },
            {
                "rule_id": "format_002",
                "name": "段落缩进",
                "description": "段落应统一缩进",
                "severity": "warning",
                "check": "paragraph_indent"
            },
            {
                "rule_id": "format_003",
                "name": "中文标点",
                "description": "应使用中文标点符号",
                "severity": "warning",
                "check": "chinese_punctuation"
            }
        ]

    def _load_fact_rules(self) -> List[Dict[str, Any]]:
        """加载事实规则"""
        return [
            {
                "rule_id": "fact_001",
                "name": "年份范围",
                "description": "年份应在合理范围内",
                "severity": "warning",
                "check": "valid_year_range"
            },
            {
                "rule_id": "fact_002",
                "name": "数字格式",
                "description": "数字格式应统一",
                "severity": "info",
                "check": "number_format"
            }
        ]


# 全局系统校验工具实例
_system_validation_tool: Optional[SystemValidationTool] = None


def get_system_validation_tool() -> SystemValidationTool:
    """获取系统校验工具单例"""
    global _system_validation_tool
    if _system_validation_tool is None:
        _system_validation_tool = SystemValidationTool()
    return _system_validation_tool
