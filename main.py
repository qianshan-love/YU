"""
县志智能编纂Agent系统 - 主入口
"""
import asyncio
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from src.agents.dispatcher import DispatcherAgent
from src.agents.task_planner_agent import TaskPlannerAgent
from src.agents.knowledge_agent import KnowledgeAgent
from src.agents.drafting_agent import DraftingAgent
from src.agents.review_agent import ReviewAgent
from src.agents.version_agent import VersionAgent
from src.agents.member_agent import MemberAgent
from src.models.state import DispatcherState
from src.utils.logger import setup_logger

# 配置日志
logger = setup_logger("main")

# 创建FastAPI应用
app = FastAPI(
    title="县志智能编纂Agent系统",
    description="基于LangGraph和ReAct模式的县志智能编纂系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== 数据模型 ==========

class StartCompilationRequest(BaseModel):
    """开始编纂请求"""
    user_id: str
    initial_requirements: Optional[Dict[str, Any]] = None
    members: Optional[List[Dict[str, Any]]] = None


class CompilationResponse(BaseModel):
    """编纂响应"""
    task_id: str
    status: str
    current_phase: str
    message: str
    data: Optional[Dict[str, Any]] = None


# ========== 初始化调度中枢 ==========

# 创建调度中枢实例
dispatcher = DispatcherAgent()

# 注册功能Agent
task_planner_agent = TaskPlannerAgent({})
knowledge_agent = KnowledgeAgent({})
drafting_agent = DraftingAgent({})
review_agent = ReviewAgent({})
version_agent = VersionAgent({})
member_agent = MemberAgent({})

dispatcher.register_agent("task_planner", task_planner_agent)
dispatcher.register_agent("knowledge", knowledge_agent)
dispatcher.register_agent("drafting", drafting_agent)
dispatcher.register_agent("review", review_agent)
dispatcher.register_agent("version", version_agent)
dispatcher.register_agent("member", member_agent)

logger.info("调度中枢初始化完成")
logger.info("已注册功能Agent: task_planner, knowledge, drafting, review, version, member")


# ========== API端点 ==========

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "县志智能编纂Agent系统",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.post("/api/v1/compilation/start", response_model=CompilationResponse)
async def start_compilation(request: StartCompilationRequest):
    """
    开始县志编纂任务

    Args:
        request: 编纂请求

    Returns:
        编纂响应
    """
    try:
        logger.info(f"收到编纂请求，用户: {request.user_id}")

        # 启动编纂任务
        state = await dispatcher.start_compilation(
            user_id=request.user_id,
            initial_requirements=request.initial_requirements,
            members=request.members
        )

        return CompilationResponse(
            task_id=state.task_id,
            status=state.current_phase.value,
            current_phase=state.current_phase.value,
            message="编纂任务已启动",
            data={
                "total_chapters": state.total_chapters,
                "catalog": [{"chapter_id": c.chapter_id, "title": c.title} for c in state.catalog],
                "members": [{"member_id": m.member_id, "name": m.name} for m in state.members]
            }
        )

    except Exception as e:
        logger.error(f"启动编纂任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动失败: {str(e)}")


@app.get("/api/v1/compilation/{task_id}/status")
async def get_compilation_status(task_id: str):
    """
    获取编纂任务状态

    Args:
        task_id: 任务ID

    Returns:
        任务状态
    """
    # 简化实现：返回示例状态
    # 实际应用中需要从数据库或缓存中查询状态
    return {
        "task_id": task_id,
        "status": "running",
        "current_phase": "chapter_drafting",
        "progress": {
            "total_chapters": 10,
            "completed_chapters": 3,
            "progress_percentage": 30
        }
    }


@app.get("/api/v1/compilation/{task_id}/result")
async def get_compilation_result(task_id: str):
    """
    获取编纂任务结果

    Args:
        task_id: 任务ID

    Returns:
        任务结果
    """
    # 简化实现：返回示例结果
    # 实际应用中需要从数据库或缓存中查询结果
    return {
        "task_id": task_id,
        "status": "completed",
        "final_draft": "县志终稿内容..."
    }


# ========== 示例使用 ==========

async def example_usage():
    """示例使用"""
    logger.info("=== 示例使用 ===")

    # 开始编纂任务
    state = await dispatcher.start_compilation(
        user_id="user001",
        initial_requirements={
            "county": "示例县",
            "purpose": "续修",
            "time_range": "2020-2025",
            "type": "综合志"
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

    logger.info(f"任务ID: {state.task_id}")
    logger.info(f"最终状态: {state.current_phase.value}")
    logger.info(f"总章节数: {state.total_chapters}")

    if state.final_draft:
        logger.info(f"终稿长度: {len(state.final_draft)} 字")


# ========== 主程序 ==========

def main():
    """主程序"""
    logger.info("启动县志智能编纂Agent系统")

    # 示例：运行示例代码
    # asyncio.run(example_usage())

    # 启动FastAPI服务
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
