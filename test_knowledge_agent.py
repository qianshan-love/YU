"""
KnowledgeAgent 功能测试脚本
"""
# -*- coding: utf-8 -*-
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Windows控制台编码修复
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from src.agents.knowledge_agent import KnowledgeAgent
from src.models.agent import AgentTask
from src.utils.logger import setup_logger

logger = setup_logger("test_knowledge")


async def test_knowledge_agent():
    """测试KnowledgeAgent功能"""

    print("=" * 60)
    print("KnowledgeAgent 功能测试")
    print("=" * 60)

    # 创建KnowledgeAgent
    knowledge_agent = KnowledgeAgent({})

    # 测试1: 查询章节撰写规范
    print("\n【测试1】查询章节撰写规范")
    task1 = AgentTask(
        task_id="test_001",
        agent_type="knowledge",
        action="query_specification",
        params={
            "spec_type": "chapter_specification",
            "chapter_type": "概述"
        },
        context={}
    )

    result1 = await knowledge_agent.execute(task1)
    print(f"  状态: {result1.status}")
    print(f"  消息: {result1.message}")
    if result1.data:
        print(f"  章节类型: {result1.data.get('chapter_type')}")
        print(f"  定位: {result1.data.get('定位')}")
        print(f"  要求: {result1.data.get('要求')}")

    # 测试2: 查询术语
    print("\n【测试2】查询术语")
    task2 = AgentTask(
        task_id="test_002",
        agent_type="knowledge",
        action="query_specification",
        params={
            "spec_type": "terminology",
            "term": "续修"
        },
        context={}
    )

    result2 = await knowledge_agent.execute(task2)
    print(f"  状态: {result2.status}")
    print(f"  消息: {result2.message}")
    if result2.data:
        print(f"  术语: {result2.data.get('term')}")
        print(f"  解释: {result2.data.get('definition')}")

    # 测试3: 检索知识
    print("\n【测试3】检索知识")
    task3 = AgentTask(
        task_id="test_003",
        agent_type="knowledge",
        action="retrieve_knowledge",
        params={
            "query": "编纂原则",
            "source": "knowledge_base",
            "limit": 3
        },
        context={}
    )

    result3 = await knowledge_agent.execute(task3)
    print(f"  状态: {result3.status}")
    print(f"  消息: {result3.message}")
    if result3.data:
        print(f"  查询: {result3.data.get('query')}")
        print(f"  结果数: {result3.data.get('total', 0)}")
        for i, item in enumerate(result3.data.get('results', [])[:2], 1):
            print(f"    结果{i}: {item.get('content')}")

    # 测试4: 检索年鉴
    print("\n【测试4】检索年鉴")
    task4 = AgentTask(
        task_id="test_004",
        agent_type="knowledge",
        action="retrieve_knowledge",
        params={
            "query": "地区生产总值",
            "source": "yearbook",
            "year": "2024",
            "limit": 3
        },
        context={}
    )

    result4 = await knowledge_agent.execute(task4)
    print(f"  状态: {result4.status}")
    print(f"  消息: {result4.message}")
    if result4.data:
        print(f"  查询: {result4.data.get('query')}")
        print(f"  年份: {result4.data.get('year')}")
        print(f"  结果数: {result4.data.get('total', 0)}")
        for i, item in enumerate(result4.data.get('results', [])[:1], 1):
            print(f"    结果{i}: {item.get('content')}")

    # 测试5: 网络搜索
    print("\n【测试5】网络搜索")
    task5 = AgentTask(
        task_id="test_005",
        agent_type="knowledge",
        action="web_search",
        params={
            "query": "示例县经济发展",
            "num_results": 3,
            "source": "mock"
        },
        context={}
    )

    result5 = await knowledge_agent.execute(task5)
    print(f"  状态: {result5.status}")
    print(f"  消息: {result5.message}")
    if result5.data:
        print(f"  查询: {result5.data.get('query')}")
        print(f"  结果数: {result5.data.get('total', 0)}")
        for i, item in enumerate(result5.data.get('results', [])[:2], 1):
            print(f"    结果{i}: {item.get('title')} - {item.get('snippet')}")

    # 测试6: 内容校验
    print("\n【测试6】内容校验")
    task6 = AgentTask(
        task_id="test_006",
        agent_type="knowledge",
        action="validate_content",
        params={
            "content": "示例县位于某省中部，总面积1234平方公里。我们认为这里经济发达。数据来源于统计局，大约有5000家企业。",
            "validation_rules": [
                "check_forbidden_words",
                "check_uncertain_expressions",
                "check_data_sources",
                "check_structure"
            ]
        },
        context={}
    )

    result6 = await knowledge_agent.execute(task6)
    print(f"  状态: {result6.status}")
    print(f"  消息: {result6.message}")
    if result6.data:
        print(f"  校验通过: {result6.data.get('passed')}")
        print(f"  错误数: {result6.data.get('error_count', 0)}")
        print(f"  警告数: {result6.data.get('warning_count', 0)}")
        if result6.data.get('errors'):
            print("  错误:")
            for error in result6.data.get('errors', []):
                print(f"    - {error}")
        if result6.data.get('warnings'):
            print("  警告:")
            for warning in result6.data.get('warnings', []):
                print(f"    - {warning}")

    # 测试7: 综合搜索
    print("\n【测试7】综合搜索")
    task7 = AgentTask(
        task_id="test_007",
        agent_type="knowledge",
        action="retrieve_knowledge",
        params={
            "query": "经济",
            "source": "comprehensive",
            "sources": ["knowledge_base", "old_annals", "yearbook"],
            "limit": 5
        },
        context={}
    )

    result7 = await knowledge_agent.execute(task7)
    print(f"  状态: {result7.status}")
    print(f"  消息: {result7.message}")
    if result7.data:
        print(f"  查询: {result7.data.get('query')}")
        print(f"  结果数: {result7.data.get('total', 0)}")
        print(f"  数据源: {result7.data.get('sources')}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


async def test_tools():
    """测试工具功能"""

    print("\n" + "=" * 60)
    print("工具功能测试")
    print("=" * 60)

    from src.tools.specification import get_specification_tool
    from src.tools.retrieval import get_retrieval_tool
    from src.tools.web_search import get_web_search_tool

    # 测试规范查询工具
    print("\n【工具1】规范查询工具")
    spec_tool = get_specification_tool()
    result = await spec_tool.query_specification("章节撰写规范", "概述")
    print(f"  状态: {result['success']}")
    print(f"  消息: {result['message']}")

    # 测试知识检索工具
    print("\n【工具2】知识检索工具")
    retrieval_tool = get_retrieval_tool()
    result = await retrieval_tool.search_knowledge_base("编纂", limit=3)
    print(f"  状态: {result['success']}")
    print(f"  消息: {result['message']}")

    # 测试网络搜索工具
    print("\n【工具3】网络搜索工具")
    web_tool = get_web_search_tool()
    result = await web_tool.search("地方志", num_results=3)
    print(f"  状态: {result['success']}")
    print(f"  消息: {result['message']}")

    print("\n" + "=" * 60)
    print("工具测试完成")
    print("=" * 60)


if __name__ == "__main__":
    # 测试KnowledgeAgent
    asyncio.run(test_knowledge_agent())

    # 测试工具
    asyncio.run(test_tools())
