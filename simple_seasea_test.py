# -*- coding: utf-8 -*-
"""
seasea 搜索简化测试
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Windows控制台编码修复
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import asyncio
from typing import Dict, Any, List

async def test_seasea_basic():
    """基础 seasea 测试"""
    print("\n" + "=" * 70)
    print("seasea 基础搜索测试")
    print("=" * 70)

    try:
        from seesea import Searcher

        # 创建搜索器（禁用日志）
        import logging
        logging.getLogger('seesea').setLevel(logging.CRITICAL)

        searcher = Searcher(region="china")
        print("  ✓ seesea 初始化成功")

        # 测试百度搜索
        print("\n  测试百度搜索...")
        query = "县志编纂"
        results = searcher.search(query, engine="baidu")

        if results:
            print(f"  ✓ 搜索成功，找到 {len(results)} 条结果")
            print(f"\n  前3条结果:")
            for i, result in enumerate(results[:3], 1):
                title = result.get('title', '')
                url = result.get('url', '')
                description = result.get('description', '')
                print(f"    {i}. {title}")
                print(f"       {url}")
                print(f"       {description[:60]}...")
        else:
            print(f"  ✗ 搜索无结果")

        # 测试Bing搜索
        print("\n  测试 Bing 搜索...")
        results = searcher.search("地方志", engine="bing")

        if results:
            print(f"  ✓ Bing 搜索成功，找到 {len(results)} 条结果")
            for i, result in enumerate(results[:2], 1):
                print(f"    {i}. {result.get('title', '')}")
        else:
            print(f"  ✗ Bing 搜索无结果")

    except ImportError as e:
        print(f"  ✗ seesea 库未安装")
        print(f"    错误: {str(e)}")
        print(f"    请运行: pip install seesea")
    except Exception as e:
        print(f"  ✗ 测试失败")
        print(f"    错误: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_web_search_tool():
    """测试 WebSearchTool"""
    print("\n" + "=" * 70)
    print("WebSearchTool seesea 集成测试")
    print("=" * 70)

    try:
        from src.tools.web_search import get_web_search_tool

        web_tool = get_web_search_tool()

        print(f"\n  可用搜索方式: {web_tool.available_search_methods}")
        print(f"  seesea 可用: {'✓' if 'seesea' in web_tool.available_search_methods else '✗'}")

        # 测试不同搜索方式
        print("\n  测试 auto 模式...")
        result = await web_tool.search("县志编纂", source="auto", engine="baidu")
        print(f"  状态: {result['success']}")
        print(f"  消息: {result['message']}")
        if result['success']:
            print(f"  数据源: {result['data']['source']}")
            print(f"  结果数: {result['data']['total']}")

        print("\n  测试 seesea 强制模式...")
        result = await web_tool.search("经济发展", source="seesea", engine="baidu")
        print(f"  状态: {result['success']}")
        print(f"  消息: {result['message']}")

        print("\n  测试 mock 模式...")
        result = await web_tool.search("人口统计", source="mock")
        print(f"  状态: {result['success']}")
        print(f"  数据源: {result['data']['source']}")

    except Exception as e:
        print(f"  ✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_knowledge_agent():
    """测试 KnowledgeAgent"""
    print("\n" + "=" * 70)
    print("KnowledgeAgent 搜索能力测试")
    print("=" * 70)

    try:
        from src.agents.knowledge_agent import KnowledgeAgent
        from src.models.agent import AgentTask

        knowledge = KnowledgeAgent({})

        print("\n  测试1：规范查询")
        task = AgentTask(
            task_id="test_001",
            agent_type="knowledge",
            action="query_specification",
            params={
                "spec_type": "chapter_specification",
                "chapter_type": "概述"
            },
            context={}
        )

        result = await knowledge.execute(task)
        print(f"  状态: {result.status}")
        print(f"  消息: {result.message}")

        print("\n  测试2：知识检索（含网络搜索）")
        task = AgentTask(
            task_id="test_002",
            agent_type="knowledge",
            action="retrieve_knowledge",
            params={
                "query": "县志编纂工作指南",
                "source": "knowledge_base",  # 会自动触发 seesea 网络搜索
                "limit": 5
            },
            context={}
        )

        result = await knowledge.execute(task)
        print(f"  状态: {result.status}")
        print(f"  消息: {result.message}")

        if result.data and result.data.get('results'):
            print(f"  查询: {result.data.get('query')}")
            print(f"  结果数: {result.data.get('total', 0)}")

            # 统计数据源
            source_count = {}
            for item in result.data['results']:
                source = item.get('source', 'unknown')
                source_count[source] = source_count.get(source, 0) + 1

            print(f"  数据源分布: {source_count}")

        print("\n  测试3：内容校验")
        test_content = "示例县位于某省中部，总面积1234平方公里，人口56万人。"
        task = AgentTask(
            task_id="test_003",
            agent_type="knowledge",
            action="validate_content",
            params={
                "content": test_content,
                "validation_rules": ["check_forbidden_words", "check_data_sources"]
            },
            context={}
        )

        result = await knowledge.execute(task)
        print(f"  状态: {result.status}")
        print(f"  消息: {result.message}")

        if result.data:
            print(f"  校验通过: {result.data.get('passed')}")
            print(f"  错误数: {result.data.get('error_count', 0)}")
            print(f"  警告数: {result.data.get('warning_count', 0)}")

    except Exception as e:
        print(f"  ✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """主测试函数"""

    print("\n" + "=" * 70)
    print("          seesea 搜索能力测试")
    print("=" * 70)

    print("\n说明:")
    print("  - 将测试 seesea 基础功能")
    print("  - 测试 WebSearchTool 集成")
    print("  - 测试 KnowledgeAgent 搜索能力")
    print("  - 验证网络搜索补充分机制")
    print("")

    try:
        # 测试1: seesea 基础功能
        await test_seasea_basic()

        # 测试2: WebSearchTool 集成
        await test_web_search_tool()

        # 测试3: KnowledgeAgent
        await test_knowledge_agent()

        print("\n" + "=" * 70)
        print("                    测试完成 ✓")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ 测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
