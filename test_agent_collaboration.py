# -*- coding: utf-8 -*-
"""
完整Agent协作流程测试
测试调度中枢与各功能Agent的协作
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

from src.agents.dispatcher import DispatcherAgent
from src.agents.task_planner_agent import TaskPlannerAgent
from src.agents.knowledge_agent import KnowledgeAgent
from src.agents.drafting_agent import DraftingAgent
from src.agents.review_agent import ReviewAgent
from src.agents.version_agent import VersionAgent
from src.agents.member_agent import MemberAgent
from src.models.state import CompilationPhase, MemberInfo
from src.models.agent import AgentTask
from src.utils.logger import setup_logger

logger = setup_logger("test_collaboration")


async def test_basic_collaboration():
    """测试基础Agent协作"""

    print("\n" + "=" * 70)
    print("【测试1】基础Agent协作测试")
    print("=" * 70)

    # 创建调度中枢
    dispatcher = DispatcherAgent()

    # 注册功能Agent
    task_planner = TaskPlannerAgent({})
    knowledge = KnowledgeAgent({})
    drafting = DraftingAgent({})
    review = ReviewAgent({})
    version = VersionAgent({})
    member = MemberAgent({})

    dispatcher.register_agent("task_planner", task_planner)
    dispatcher.register_agent("knowledge", knowledge)
    dispatcher.register_agent("drafting", drafting)
    dispatcher.register_agent("review", review)
    dispatcher.register_agent("version", version)
    dispatcher.register_agent("member", member)

    print("\n1.1 调度中枢初始化")
    print(f"  已注册Agent: {list(dispatcher.agents.keys())}")

    # 测试单个Agent调用
    print("\n1.2 测试单个Agent调用")
    from src.models.agent import AgentTask

    # 测试KnowledgeAgent
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

    result = await dispatcher._invoke_agent(task)
    print(f"  KnowledgeAgent调用: {result.status}")
    print(f"  消息: {result.message}")

    # 测试DraftingAgent
    task = AgentTask(
        task_id="test_002",
        agent_type="drafting",
        action="draft_chapter",
        params={
            "chapter_id": "ch01",
            "chapter_title": "概述",
            "catalog": [
                {"chapter_id": "ch01", "title": "概述"}
            ]
        },
        context={}
    )

    result = await dispatcher._invoke_agent(task)
    print(f"  DraftingAgent调用: {result.status}")
    print(f"  消息: {result.message}")

    # 测试ReviewAgent
    task = AgentTask(
        task_id="test_003",
        agent_type="review",
        action="review_chapter",
        params={
            "chapter_id": "ch01",
            "draft": "测试内容",
            "reviewers": ["user001"],
            "versions": []
        },
        context={}
    )

    result = await dispatcher._invoke_agent(task)
    print(f"  ReviewAgent调用: {result.status}")
    print(f"  消息: {result.message}")


async def test_state_transitions():
    """测试状态转换"""

    print("\n" + "=" * 70)
    print("【测试2】状态转换测试")
    print("=" * 70)

    # 创建调度中枢
    dispatcher = DispatcherAgent()

    # 注册功能Agent
    dispatcher.register_agent("task_planner", TaskPlannerAgent({}))
    dispatcher.register_agent("knowledge", KnowledgeAgent({}))
    dispatcher.register_agent("drafting", DraftingAgent({}))
    dispatcher.register_agent("review", ReviewAgent({}))
    dispatcher.register_agent("version", VersionAgent({}))
    dispatcher.register_agent("member", MemberAgent({}))

    print("\n2.1 测试状态转换路由")

    # 测试目录生成路由
    print("\n  测试用例 1: 目录生成路由")
    state_dict = {
        "current_phase": CompilationPhase.CATALOG_GENERATION.value,
        "catalog": [{"chapter_id": "ch01", "title": "概述"}]
    }

    try:
        route = dispatcher._route_from_catalog(state_dict)
        print(f"    当前阶段: {state_dict['current_phase']}")
        print(f"    下一阶段: {route}")
        print(f"    结果: {'✓' if route == 'task_assignment' else '✗'}")
    except Exception as e:
        print(f"    错误: {str(e)}")

    # 测试章节起草路由
    print("\n  测试用例 2: 章节起草路由（全部完成）")
    state_dict = {
        "current_phase": CompilationPhase.CHAPTER_DRAFTING.value,
        "chapters": {
            "ch01": {"chapter_id": "ch01", "status": "reviewed"},
            "ch02": {"chapter_id": "ch02", "status": "reviewed"}
        }
    }

    try:
        route = dispatcher._route_from_drafting(state_dict)
        print(f"    当前阶段: {state_dict['current_phase']}")
        print(f"    下一阶段: {route}")
        print(f"    结果: {'✓' if route == 'final_review' else '✗'}")
    except Exception as e:
        print(f"    错误: {str(e)}")

    print("\n  测试用例 3: 章节起草路由（有待审核）")
    state_dict = {
        "current_phase": CompilationPhase.CHAPTER_DRAFTING.value,
        "chapters": {
            "ch01": {"chapter_id": "ch01", "status": "drafted"},
            "ch02": {"chapter_id": "ch02", "status": "reviewed"}
        }
    }

    try:
        route = dispatcher._route_from_drafting(state_dict)
        print(f"    当前阶段: {state_dict['current_phase']}")
        print(f"    下一阶段: {route}")
        print(f"    结果: {'✓' if route == 'chapter_review' else '✗'}")
    except Exception as e:
        print(f"    错误: {str(e)}")


async def test_full_workflow():
    """测试完整工作流程（简化版）"""

    print("\n" + "=" * 70)
    print("【测试3】完整工作流程测试（简化版）")
    print("=" * 70)

    # 创建调度中枢
    dispatcher = DispatcherAgent()

    # 注册功能Agent
    dispatcher.register_agent("task_planner", TaskPlannerAgent({}))
    dispatcher.register_agent("knowledge", KnowledgeAgent({}))
    dispatcher.register_agent("drafting", DraftingAgent({}))
    dispatcher.register_agent("review", ReviewAgent({}))
    dispatcher.register_agent("version", VersionAgent({}))
    dispatcher.register_agent("member", MemberAgent({}))

    print("\n3.1 启动简化编纂流程")

    # 启动编纂任务（只执行前几个阶段）
    try:
        state = await dispatcher.start_compilation(
            user_id="user001",
            initial_requirements={
                "county": "示例县",
                "purpose": "续修",
                "time_range": "2020-2025",
                "type": "综合志",
                "confirmed": True  # 自动确认，跳过用户交互
            },
            members=[
                {
                    "member_id": "user001",
                    "name": "张三",
                    "role": "editor",
                    "expertise": ["经济", "政治"]
                },
                {
                    "member_id": "user002",
                    "name": "李四",
                    "role": "reviewer",
                    "expertise": ["文化", "社会"]
                }
            ]
        )

        print(f"\n3.2 执行结果")
        print(f"  任务ID: {state.task_id}")
        print(f"  用户ID: {state.user_id}")
        print(f"  当前阶段: {state.current_phase.value}")
        print(f"  总章节数: {state.total_chapters}")

        print(f"\n3.3 章节信息")
        for i, chapter in enumerate(state.catalog[:3], 1):
            print(f"  {i}. {chapter.chapter_id}: {chapter.title}")

        print(f"\n3.4 成员信息")
        for member in state.members:
            print(f"  - {member.name} ({member.role})")

        print(f"\n3.5 任务分配")
        for chapter_id, assignment in list(state.task_assignments.items())[:3]:
            print(f"  {chapter_id}:")
            print(f"    撰稿人: {', '.join(assignment.drafters)}")
            print(f"    审核人: {', '.join(assignment.reviewers)}")

        print(f"\n3.6 章节状态")
        for chapter_id, chapter_state in list(state.chapters.items())[:3]:
            print(f"  {chapter_id}: {chapter_state.status}")

        # 检查是否有错误
        if state.errors:
            print(f"\n3.7 错误记录")
            for error in state.errors[:3]:
                print(f"  - [{error.error_type}] {error.error_message}")

    except Exception as e:
        print(f"\n  错误: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_agent_dependency():
    """测试Agent依赖关系"""

    print("\n" + "=" * 70)
    print("【测试4】Agent依赖关系测试")
    print("=" * 70)

    # 创建Agents
    knowledge = KnowledgeAgent({})
    drafting = DraftingAgent({})
    review = ReviewAgent({})

    print("\n4.1 DraftingAgent 依赖 KnowledgeAgent")

    # 模拟DraftingAgent调用KnowledgeAgent
    task = AgentTask(
        task_id="dep_test_001",
        agent_type="knowledge",
        action="retrieve_knowledge",
        params={
            "query": "概述撰写规范",
            "source": "knowledge_base",
            "limit": 3
        },
        context={}
    )

    result = await knowledge.execute(task)
    print(f"  状态: {result.status}")
    print(f"  消息: {result.message}")
    if result.data:
        print(f"  结果数: {result.data.get('total', 0)}")

    print("\n4.2 ReviewAgent 依赖 KnowledgeAgent")

    # 模拟ReviewAgent调用KnowledgeAgent
    task = AgentTask(
        task_id="dep_test_002",
        agent_type="knowledge",
        action="validate_content",
        params={
            "content": "示例县位于某省中部，总面积1234平方公里。",
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


async def test_parallel_execution():
    """测试并行执行"""

    print("\n" + "=" * 70)
    print("【测试5】并行执行测试")
    print("=" * 70)

    knowledge = KnowledgeAgent({})
    drafting = DraftingAgent({})
    review = ReviewAgent({})

    print("\n5.1 并行执行多个Agent任务")

    # 创建多个任务
    tasks = [
        # KnowledgeAgent任务
        AgentTask(
            task_id="parallel_001",
            agent_type="knowledge",
            action="query_specification",
            params={
                "spec_type": "chapter_specification",
                "chapter_type": "概述"
            },
            context={}
        ),
        # DraftingAgent任务
        AgentTask(
            task_id="parallel_002",
            agent_type="drafting",
            action="draft_chapter",
            params={
                "chapter_id": "ch01",
                "chapter_title": "概述",
                "catalog": [{"chapter_id": "ch01", "title": "概述"}]
            },
            context={}
        ),
        # ReviewAgent任务
        AgentTask(
            task_id="parallel_003",
            agent_type="review",
            action="review_chapter",
            params={
                "chapter_id": "ch01",
                "draft": "测试内容",
                "reviewers": ["user001"],
                "versions": []
            },
            context={}
        )
    ]

    # 并行执行
    import time
    start_time = time.time()

    results = await asyncio.gather(
        knowledge.execute(tasks[0]),
        drafting.execute(tasks[1]),
        review.execute(tasks[2])
    )

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"\n5.2 执行结果")
    print(f"  总耗时: {execution_time:.2f}秒")

    for i, result in enumerate(results, 1):
        print(f"\n  任务 {i}:")
        print(f"    Agent: {result.agent_type}")
        print(f"    状态: {result.status}")
        print(f"    消息: {result.message}")


async def main():
    """主测试函数"""

    print("\n" + "=" * 70)
    print("          完整Agent协作流程测试")
    print("=" * 70)

    try:
        # 测试1: 基础Agent协作
        await test_basic_collaboration()

        # 测试2: 状态转换
        await test_state_transitions()

        # 测试3: 完整工作流程
        await test_full_workflow()

        # 测试4: Agent依赖关系
        await test_agent_dependency()

        # 测试5: 并行执行
        await test_parallel_execution()

        print("\n" + "=" * 70)
        print("                    测试完成 ✓")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ 测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
