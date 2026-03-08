"""
通用工具函数
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List


def generate_task_id() -> str:
    """生成任务ID"""
    return f"task_{uuid.uuid4().hex[:16]}_{int(datetime.now().timestamp())}"


def generate_version_id(chapter_id: str, version_number: int) -> str:
    """生成版本ID"""
    timestamp = int(datetime.now().timestamp())
    return f"{chapter_id}_v{version_number:03d}_{timestamp}"


def generate_agent_id(agent_type: str) -> str:
    """生成Agent ID"""
    return f"{agent_type}_{uuid.uuid4().hex[:8]}"


def safe_get(data: Dict[str, Any], *keys, default: Any = None) -> Any:
    """
    安全获取嵌套字典值

    Args:
        data: 字典数据
        *keys: 键路径
        default: 默认值

    Returns:
        获取到的值或默认值
    """
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return default
    return data


def flatten_list(nested_list: List[Any]) -> List[Any]:
    """
    展平嵌套列表

    Args:
        nested_list: 嵌套列表

    Returns:
        展平后的列表
    """
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    将列表分块

    Args:
        items: 列表
        chunk_size: 块大小

    Returns:
        分块后的列表
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并多个字典（深度合并）

    Args:
        *dicts: 字典列表

    Returns:
        合并后的字典
    """
    result = {}
    for d in dicts:
        for key, value in d.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_dicts(result[key], value)
            else:
                result[key] = value
    return result


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本

    Args:
        text: 文本
        max_length: 最大长度
        suffix: 后缀

    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_timestamp(dt: datetime) -> str:
    """
    格式化时间戳

    Args:
        dt: 日期时间

    Returns:
        格式化后的字符串
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_timestamp(timestamp_str: str) -> datetime:
    """
    解析时间戳字符串

    Args:
        timestamp_str: 时间戳字符串

    Returns:
        日期时间对象
    """
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"无法解析时间戳: {timestamp_str}")
