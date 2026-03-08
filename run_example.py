"""
示例运行脚本
演示如何使用县志智能编纂Agent系统
"""
import asyncio
from main import dispatcher

async def run_example():
    """运行示例"""

    print("=" * 60)
    print("县志智能编纂Agent系统 - 示例运行")
    print("=" * 60)

    # 开始编纂任务
    print("\n【1】开始编纂任务...")

    state = await dispatcher.start_compilation(
        user_id="user001",
        initial_requirements={
            "county": "示例县",
            "purpose": "续修",
            "time_range": "2020-2025",
            "type": "综合志",
            "confirmed": True  # 自动确认，用于示例演示
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

    print(f"  任务ID: {state.task_id}")
    print(f"  用户ID: {state.user_id}")
    print(f"  创建时间: {state.created_at}")

    # 显示目录
    print("\n【2】生成的县志目录：")
    for i, chapter in enumerate(state.catalog, 1):
        print(f"  {i}. {chapter.chapter_id}: {chapter.title}")

    # 显示成员
    print("\n【3】参与成员：")
    for member in state.members:
        print(f"  - {member.name} ({member.role})")

    # 显示任务分配
    print("\n【4】任务分配：")
    for chapter_id, assignment in state.task_assignments.items():
        print(f"  {chapter_id}:")
        print(f"    撰稿人: {', '.join(assignment.drafters)}")
        print(f"    审核人: {', '.join(assignment.reviewers)}")

    # 显示章节状态
    print("\n【5】章节执行状态：")
    for chapter_id, chapter_state in state.chapters.items():
        print(f"  {chapter_id}: {chapter_state.status}")

    # 显示版本信息
    print("\n【6】版本信息：")
    for chapter_id, versions in state.versions.items():
        if versions:
            latest = versions[-1]
            print(f"  {chapter_id}: {latest.version_id} ({latest.version_type})")
            print(f"    字数: {len(latest.content)}")

    # 显示审核记录
    if state.review_records:
        print("\n【7】审核记录：")
        for record in state.review_records:
            print(f"  {record.chapter_id}: {record.status} - {record.comments}")

    # 显示终稿
    if state.final_draft:
        print("\n【8】终稿信息：")
        print(f"  字数: {len(state.final_draft)}")
        print(f"  前500字: {state.final_draft[:500]}...")

    # 显示执行日志
    if state.execution_logs:
        print("\n【9】执行日志（最后3条）：")
        for log in state.execution_logs[-3:]:
            print(f"  [{log.agent_type}] {log.action}: {log.status}")

    # 显示错误
    if state.errors:
        print("\n【10】错误记录：")
        for error in state.errors:
            print(f"  [{error.error_type}] {error.error_message}")

    # 最终状态
    print("\n【11】最终状态：")
    print(f"  当前阶段: {state.current_phase.value}")
    print(f"  是否归档: {state.archived}")

    print("\n" + "=" * 60)
    print("示例运行完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_example())
