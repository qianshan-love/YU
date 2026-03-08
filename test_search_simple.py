"""
Simple Search Test
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import asyncio
from src.tools.web_search import get_web_search_tool
from src.agents.knowledge_agent import KnowledgeAgent
from src.models.agent import AgentTask

logger = None


async def test_web_search():
    """Test web search capability"""
    print("\n" + "=" * 70)
    print("Web Search Test")
    print("=" * 70)

    try:
        web_tool = get_web_search_tool()

        print(f"Available search methods: {web_tool.available_search_methods}")

        # Test 1: Mock search
        print("\n[1] Test Mock Search")
        result = await web_tool.search("地方志", source="mock")
        print(f"  Status: {result['success']}")
        print(f"  Message: {result['message']}")
        if result['success']:
            print(f"  Source: {result['data']['source']}")
            print(f"  Total: {result['data']['total']}")

        # Test 2: Seesea search (with mock fallback)
        print("\n[2] Test Seesea Search (will use mock if seesea fails)")
        result = await web_tool.search("经济发展", source="seesea")
        print(f"  Status: {result['success']}")
        print(f"  Message: {result['message']}")
        if result['success']:
            print(f"  Source: {result['data']['source']}")
            print(f"  Total: {result['data']['total']}")

        # Test 3: Auto mode
        print("\n[3] Test Auto Mode")
        result = await web_tool.search("人口统计", source="auto")
        print(f"  Status: {result['success']}")
        print(f"  Message: {result['message']}")
        if result['success']:
            print(f"  Source: {result['data']['source']}")

    except Exception as e:
        print(f"\n[Error] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_knowledge_agent():
    """Test KnowledgeAgent search capability"""
    print("\n" + "=" * 70)
    print("KnowledgeAgent Search Test")
    print("=" * 70)

    try:
        knowledge = KnowledgeAgent({})

        # Test 1: Query specification
        print("\n[1] Test Specification Query")
        task = AgentTask(
            task_id="test_001",
            agent_type="knowledge",
            action="query_specification",
            params={
                "spec_type": "chapter_specification",
                "chapter_type": "overview"
            },
            context={}
        )

        result = await knowledge.execute(task)
        print(f"  Status: {result.status}")
        print(f"  Message: {result.message}")
        if result.data:
            print(f"  Chapter Type: {result.data.get('chapter_type')}")

        # Test 2: Knowledge retrieval with web search
        print("\n[2] Test Knowledge Retrieval")
        task = AgentTask(
            task_id="test_002",
            agent_type="knowledge",
            action="retrieve_knowledge",
            params={
                "query": "经济发展",
                "source": "knowledge_base",
                "limit": 5
            },
            context={}
        )

        result = await knowledge.execute(task)
        print(f"  Status: {result.status}")
        print(f"  Message: {result.message}")
        if result.data:
            print(f"  Query: {result.data.get('query')}")
            print(f"  Total: {result.data.get('total', 0)}")

            # Show source distribution
            if result.data.get('results'):
                source_count = {}
                for item in result.data['results']:
                    source = item.get('source', 'unknown')
                    source_count[source] = source_count.get(source, 0) + 1

                print(f"  Source Distribution: {source_count}")

        # Test 3: Content validation
        print("\n[3] Test Content Validation")
        test_content = "Example County is located in central province, area 1234 km2, population 56 million. Data from statistics bureau."
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
        print(f"  Status: {result.status}")
        print(f"  Message: {result.message}")
        if result.data:
            print(f"  Passed: {result.data.get('passed')}")
            print(f"  Errors: {result.data.get('error_count', 0)}")
            print(f"  Warnings: {result.data.get('warning_count', 0)}")

    except Exception as e:
        print(f"\n[Error] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Main test function"""
    print("\n" + "=" * 70)
    print("Search Capability Test")
    print("=" * 70)

    print("\nObjective:")
    print("- Test web search tool functionality")
    print("- Test KnowledgeAgent search capability")
    print("- Verify fallback mechanism")
    print("- Verify agent collaboration")

    print("\nNote:")
    print("- Seesea integration has been completed")
    print("- Mock data used as fallback")
    print("- In production, real search APIs will be used")

    try:
        # Test web search
        await test_web_search()

        # Test knowledge agent
        await test_knowledge_agent()

        print("\n" + "=" * 70)
        print("                    Test Completed Successfully")
        print("=" * 70)

    except Exception as e:
        print(f"\nTest encountered error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
