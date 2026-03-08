# -*- coding: utf-8 -*-
"""
seesea 搜索引擎测试
"""
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

from src.tools.web_search import get_web_search_tool
from src.agents.knowledge_agent import KnowledgeAgent
from src.models.agent import AgentTask
from src.utils.logger import setup_logger

logger = setup_logger("test_seasea")


async def test_seasea_availability():
    """测试 seesea 可用性"""

    print("\n" + "=" * 70)
    print("【测试1】seasea 可用性测试")
    print("=" * 70)

    # 检查 seesea 是否安装
    try:
        from seesea import Searcher
        print("  ✓ seasea 库已安装")
    except ImportError:
        print("  ✗ seasea 库未安装")
        print("    请运行: pip install seesea")
        return

    # 创建搜索器
    print("\n  创建搜索器...")
    searcher = Searcher(region="china")
    print("  ✓ 搜索器创建成功")

    # 测试搜索
    print("\n  测试搜索...")
    query = "县志编纂"
    results = searcher.search(query, engine="baidu")

    if results:
        print(f"  ✓ 搜索成功，找到 {len(results)} 条结果")
        print(f"\n  前3条结果:")
        for i, result in enumerate(results[:3], 1):
            print(f"    {i}. {result.get('title', '')}")
            print(f"       URL: {result.get('url', '')}")
            print(f"       描述: {result.get('description', '')[:50]}...")
    else:
        print(f"  ✗ 搜索无结果")


async def test_web_search_tool_seasea():
    """测试 WebSearchTool 的 seasea 集成"""

    print("\n" + "=" * 70)
    print("【测试2】WebSearchTool seasea 集成测试")
    print("=" * 70)

    web_tool = get_web_search_tool()

    print(f"\n  可用搜索方式: {web_tool.available_search_methods}")
    print(f"  seasea 可用: {'✓' if 'seasea' in web_tool.available_search_methods else '✗'}")

    # 测试不同搜索引擎
    engines = ["baidu", "bing", "360", "so"]
    queries = ["县志编纂", "经济发展", "人口统计"]

    for engine in engines:
        print(f"\n  测试引擎: {engine}")
        for query in queries:
            result = await web_tool.search(query, source="seesea", engine=engine)
            print(f"    查询 '{query}': {result['data']['total']} 条结果, 状态: {result['status']}")


async def test_knowledge_agent_with_seasea():
    """测试 KnowledgeAgent 使用 seasea"""

    print("\n" + "=" * 70)
    print("【测试3】KnowledgeAgent seasea 集成测试")
    print("=" * 70)

    knowledge_agent = KnowledgeAgent({})

    # 测试知识检索
    print("\n  测试知识检索（含 seasea 网络搜索）")
    task = AgentTask(
        task_id="test_seasea_001",
        agent_type="knowledge",
        action="retrieve_knowledge",
        params={
            "query": "县志编纂工作指南",
            "source": "knowledge_base",  # 会自动触发 seasea 网络搜索
            "limit": 5
        },
        context={}
    )

    result = await knowledge_agent.execute(task)
    print(f"  状态: {result.status}")
    print(f"  消息: {result.message}")

    if result.data:
        print(f"  查询: {result.data.get('query')}")
        print(f"  结果数: {result.data.get('total', 0)}")

        # 统计各数据源结果
        source_count = {}
        for item in result.data.get('results', []):
            source = item.get('source', 'unknown')
            source_count[source] = source_count.get(source, 0) + 1

        print(f"  数据源分布: {source_count}")


async def test_batch_search():
    """测试批量搜索"""

    print("\n" + "=" * 70)
    print("【测试4】批量搜索测试")
    print("=" * 70)

    web_tool = get_web_search_tool()

    queries = [
        "县志编纂规范",
        "地方志编纂",
        "县志体例",
        "经济发展统计",
        "人口普查数据"
    ]

    print("\n  批量搜索测试...")
    import time
    start_time = time.time()

    results = await web_tool.batch_search(queries, num_results=3, source="seasea")

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"\n  总耗时: {execution_time:.2f}秒")
    print(f"  查询数: {len(queries)}")

    for i, (query, search_result) in enumerate(results['data']['results'].items(), 1):
        print(f"\n  查询 {i}: {query}")
        print(f"    状态: {search_result['status']}")
        print(f"    结果数: {search_result['data']['total']}")


async def test_engine_comparison():
    """测试不同搜索引擎对比"""

    print("\n" + "=" * 70)
    print("【测试5】搜索引擎对比测试")
    print("=" * 70)

    web_tool = get_web_search_tool()

    query = "县志编纂"
    engines = ["baidu", "bing", "360"]

    print(f"\n  查询关键词: {query}\n")

    for engine in engines:
        result = await web_tool.search(query, source="seasea", engine=engine)
        print(f"\n  引擎: {engine}")
        print(f"    状态: {result['status']}")
        print(f"    消息: {result['message']}")

        if result['success']:
            results = result['data']['results']
            print(f"    结果数: {len(results)}")

            if results:
                print(f"    首条结果:")
                print(f"      标题: {results[0].get('title', '')}")
                print(f"      来源: {results[0].get('source', '')}")


async def test_fallback_mechanism():
    """测试降级机制"""

    print("\n" + "=" * 70)
    print("【测试6】降级机制测试")
    print("=" * 70)

    web_tool = get_web_search_tool()

    # 测试不同的 source 选项
    test_cases = [
        {"source": "auto", "desc": "自动选择（优先 seasea）"},
        {"source": "seasea", "desc": "强制使用 seasea"},
        {"source": "bing", "desc": "强制使用 Bing API"},
        {"source": "google", "desc": "强制使用 Google API"},
        {"source": "mock", "desc": "使用模拟数据"}
    ]

    query = "地方志编纂"

    print(f"\n  测试查询: {query}\n")

    for i, case in enumerate(test_cases, 1):
        print(f"  测试用例 {i}: {case['desc']}")
        result = await web_tool.search(query, source=case['source'], engine="baidu")
        print(f"    状态: {result['status']}")
        print(f"    数据源: {result['data'].get('source', 'unknown')}")
        print(f"    结果数: {result['data'].get('total', 0)}")


async def main():
    """主测试函数"""

    print("\n" + "=" * 70)
    print("          seasea 搜索引擎集成测试")
    print("=" * 70)

    try:
        # 测试1: seasea 可用性
        await test_seasea_availability()

        # 测试2: WebSearchTool seasea 集成
        await test_web_search_tool_seasea()

        # 测试3: KnowledgeAgent seasea 集成
        await test_knowledge_agent_with_seasea()

        # 测试4: 批量搜索
        await test_batch_search()

        # 测试5: 搜索引擎对比
        await test_engine_comparison()

        # 测试6: 降级机制
        await test_fallback_mechanism()

        print("\n" + "=" * 70)
        print("                    测试完成 ✓")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ 测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
