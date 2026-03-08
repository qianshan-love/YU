"""
KnowledgeAgent 网络搜索能力测试
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
from src.tools.web_search import get_web_search_tool
from src.tools.retrieval import get_retrieval_tool
from src.utils.logger import setup_logger

logger = setup_logger("test_network_search")


async def test_web_search_tool():
    """测试网络搜索工具"""

    print("\n" + "=" * 70)
    print("【测试1】网络搜索工具 - 直接测试")
    print("=" * 70)

    web_tool = get_web_search_tool()

    # 测试1: 基本搜索
    print("\n1.1 基本搜索测试")
    query = "地方志编纂"
    print(f"  查询关键词: {query}")

    result = await web_tool.search(query, num_results=5, source="mock")
    print(f"  状态: {result['success']}")
    print(f"  消息: {result['message']}")

    if result['success']:
        data = result['data']
        print(f"  结果数量: {data['total']}")
        print(f"  数据源: {data['source']}")

        for i, item in enumerate(data['results'], 1):
            print(f"\n  结果 {i}:")
            print(f"    标题: {item['title']}")
            print(f"    URL: {item['url']}")
            print(f"    摘要: {item['snippet']}")
            print(f"    来源: {item['source']}")

    # 测试2: 批量搜索
    print("\n1.2 批量搜索测试")
    queries = ["县志体例", "经济发展", "人口统计"]
    print(f"  查询列表: {queries}")

    result = await web_tool.batch_search(queries, num_results=3)
    print(f"  状态: {result['success']}")
    print(f"  消息: {result['message']}")

    if result['success']:
        data = result['data']
        print(f"  总查询数: {data['total_queries']}")

        for query, search_result in data['results'].items():
            print(f"\n  查询 '{query}':")
            print(f"    状态: {search_result['success']}")
            print(f"    结果数: {search_result['data']['total']}")


async def test_retrieval_with_fallback():
    """测试检索与网络搜索补充"""

    print("\n" + "=" * 70)
    print("【测试2】知识检索 + 网络搜索补充")
    print("=" * 70)

    retrieval_tool = get_retrieval_tool()

    # 测试: 先检索知识库，如果无结果则网络搜索
    print("\n2.1 智能检索测试")
    query = "地方志编纂原则"
    print(f"  查询关键词: {query}")

    # 第一步：知识库检索
    print("\n  第一步：知识库检索")
    kb_result = await retrieval_tool.search_knowledge_base(query, limit=3)
    print(f"    状态: {kb_result['success']}")
    print(f"    结果数: {kb_result['data']['total']}")

    # 第二步：如果知识库结果少，补充网络搜索
    if kb_result['success'] and kb_result['data']['total'] < 3:
        print(f"\n  第二步：知识库结果不足，触发网络搜索补充")
        web_tool = get_web_search_tool()
        web_result = await web_tool.search(query, num_results=3)

        if web_result['success']:
            print(f"    网络搜索结果数: {web_result['data']['total']}")

            # 合并结果
            all_results = kb_result['data']['results'] + web_result['data']['results']
            print(f"    合并后结果总数: {len(all_results)}")

            print(f"\n  最终结果:")
            for i, item in enumerate(all_results[:5], 1):
                source = item.get('source', 'unknown')
                print(f"    {i}. [{source}] {item.get('content', item.get('snippet', ''))}")


async def test_knowledge_agent_web_search():
    """测试KnowledgeAgent的网络搜索能力"""

    print("\n" + "=" * 70)
    print("【测试3】KnowledgeAgent - 网络搜索功能")
    print("=" * 70)

    knowledge_agent = KnowledgeAgent({})

    # 测试1: 直接网络搜索
    print("\n3.1 直接网络搜索")
    task = AgentTask(
        task_id="test_web_001",
        agent_type="knowledge",
        action="web_search",
        params={
            "query": "地方志编纂工作指南",
            "num_results": 5,
            "source": "mock"
        },
        context={}
    )

    result = await knowledge_agent.execute(task)
    print(f"  状态: {result.status}")
    print(f"  消息: {result.message}")

    if result.status == "success" and result.data:
        print(f"  查询: {result.data.get('query')}")
        print(f"  结果数: {result.data.get('total', 0)}")

        for i, item in enumerate(result.data.get('results', [])[:3], 1):
            print(f"\n  结果 {i}:")
            print(f"    标题: {item.get('title')}")
            print(f"    摘要: {item.get('snippet')}")
            print(f"    来源: {item.get('source')}")

    # 测试2: 知识检索（会自动触发网络搜索补充）
    print("\n\n3.2 知识检索（含自动网络搜索补充）")
    task = AgentTask(
        task_id="test_retrieve_001",
        agent_type="knowledge",
        action="retrieve_knowledge",
        params={
            "query": "示例县经济发展情况",
            "source": "knowledge_base",
            "limit": 5
        },
        context={}
    )

    result = await knowledge_agent.execute(task)
    print(f"  状态: {result.status}")
    print(f"  消息: {result.message}")

    if result.status == "success" and result.data:
        print(f"  查询: {result.data.get('query')}")
        print(f"  结果数: {result.data.get('total', 0)}")

        # 统计各数据源的结果
        source_count = {}
        for item in result.data.get('results', []):
            source = item.get('source', 'unknown')
            source_count[source] = source_count.get(source, 0) + 1

        print(f"  数据源分布: {source_count}")

        print(f"\n  结果:")
        for i, item in enumerate(result.data.get('results', [])[:5], 1):
            source = item.get('source', 'unknown')
            content = item.get('content', item.get('snippet', ''))
            print(f"    {i}. [{source}] {content}")


async def test_real_world_scenarios():
    """测试真实场景"""

    print("\n" + "=" * 70)
    print("【测试4】真实应用场景测试")
    print("=" * 70)

    knowledge_agent = KnowledgeAgent({})

    # 场景1: 撰稿前查询规范
    print("\n4.1 撰稿前查询规范")
    task = AgentTask(
        task_id="scenario_001",
        agent_type="knowledge",
        action="query_specification",
        params={
            "spec_type": "chapter_specification",
            "chapter_type": "经济"
        },
        context={}
    )

    result = await knowledge_agent.execute(task)
    print(f"  状态: {result.status}")
    if result.status == "success" and result.data:
        print(f"  章节: {result.data.get('chapter_type')}")
        print(f"  定位: {result.data.get('定位')}")
        print(f"  要求: {result.data.get('requirements')}")

    # 场景2: 检索相关资料（含网络搜索）
    print("\n4.2 检索相关资料")
    task = AgentTask(
        task_id="scenario_002",
        agent_type="knowledge",
        action="retrieve_knowledge",
        params={
            "query": "经济发展数据",
            "source": "comprehensive",
            "limit": 5
        },
        context={}
    )

    result = await knowledge_agent.execute(task)
    print(f"  状态: {result.status}")
    print(f"  消息: {result.message}")
    if result.status == "success" and result.data:
        print(f"  结果数: {result.data.get('total', 0)}")

    # 场景3: 检索无结果时触发网络搜索
    print("\n4.3 检索无结果时触发网络搜索")
    task = AgentTask(
        task_id="scenario_003",
        agent_type="knowledge",
        action="retrieve_knowledge",
        params={
            "query": "地方志编纂最新政策",  # 知识库可能没有这个
            "source": "knowledge_base",
            "limit": 3
        },
        context={}
    )

    result = await knowledge_agent.execute(task)
    print(f"  状态: {result.status}")
    print(f"  消息: {result.message}")
    if result.status == "success" and result.data:
        print(f"  查询: {result.data.get('query')}")
        print(f"  结果数: {result.data.get('total', 0)}")

        # 统计数据源
        sources = set()
        for item in result.data.get('results', []):
            sources.add(item.get('source', 'unknown'))

        print(f"  使用的数据源: {sources}")
        if 'Bing' in sources or 'mock' in sources:
            print(f"  ✅ 已触发网络搜索补充")


async def main():
    """主测试函数"""

    print("\n" + "=" * 70)
    print("          KnowledgeAgent 网络搜索能力测试")
    print("=" * 70)

    try:
        # 测试1: 网络搜索工具
        await test_web_search_tool()

        # 测试2: 知识检索 + 网络搜索补充
        await test_retrieval_with_fallback()

        # 测试3: KnowledgeAgent网络搜索功能
        await test_knowledge_agent_web_search()

        # 测试4: 真实场景
        await test_real_world_scenarios()

        print("\n" + "=" * 70)
        print("                    测试完成 ✅")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
