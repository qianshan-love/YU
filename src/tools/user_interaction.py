"""
用户交互工具
用于与用户进行交互，收集需求、反馈等
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class UserInteractionTool:
    """用户交互工具"""

    def __init__(self):
        """初始化用户交互工具"""
        # 内存存储（实际项目应使用WebSocket等实时通信）
        self.user_sessions = {}  # {user_id: UserSession}
        self.pending_questions = {}  # {task_id: Question}
        self.question_history = {}  # {task_id: [QuestionRecord]}

        logger.info("用户交互工具初始化完成")

    async def ask_question(
        self,
        user_id: str,
        task_id: str,
        question: str,
        question_type: str = "text",
        options: Optional[List[str]] = None,
        required: bool = True
    ) -> Dict[str, Any]:
        """
        向用户提问

        Args:
            user_id: 用户ID
            task_id: 任务ID
            question: 问题内容
            question_type: 问题类型（text/choice/confirmation/file_upload）
            options: 选项（用于choice类型）
            required: 是否必须回答

        Returns:
            提问结果
        """
        try:
            question_id = f"q_{datetime.now().timestamp()}"

            question_data = {
                "question_id": question_id,
                "task_id": task_id,
                "question": question,
                "question_type": question_type,
                "options": options,
                "required": required,
                "asked_at": datetime.now().isoformat(),
                "status": "pending",
                "answer": None
            }

            # 保存待回答的问题
            if task_id not in self.pending_questions:
                self.pending_questions[task_id] = []

            self.pending_questions[task_id].append(question_data)

            # 保存到用户会话
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = {
                    "user_id": user_id,
                    "created_at": datetime.now().isoformat(),
                    "questions": []
                }

            self.user_sessions[user_id]["questions"].append(question_data)

            logger.info(f"向用户提问: {user_id}, 问题: {question[:50]}...")

            return {
                "success": True,
                "question_id": question_id,
                "question": question,
                "question_type": question_type,
                "options": options,
                "required": required,
                "status": "pending",
                "asked_at": question_data["asked_at"],
                "message": "问题已发送给用户"
            }

        except Exception as e:
            logger.error(f"提问异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "提问异常"
            }

    async def receive_answer(
        self,
        question_id: str,
        answer: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        接收用户回答

        Args:
            question_id: 问题ID
            answer: 用户回答
            user_id: 用户ID

        Returns:
            接收结果
        """
        try:
            # 查找问题
            found_question = None
            for task_id, questions in self.pending_questions.items():
                for q in questions:
                    if q["question_id"] == question_id:
                        found_question = q
                        break
                if found_question:
                    break

            if not found_question:
                return {
                    "success": False,
                    "error": "问题不存在",
                    "message": f"问题 {question_id} 不存在或已过期"
                }

            # 更新问题状态
            found_question["answer"] = answer
            found_question["status"] = "answered"
            found_question["answered_at"] = datetime.now().isoformat()
            found_question["answered_by"] = user_id

            # 保存到历史记录
            task_id = found_question["task_id"]
            if task_id not in self.question_history:
                self.question_history[task_id] = []

            self.question_history[task_id].append({
                "question": found_question["question"],
                "answer": answer,
                "question_type": found_question["question_type"],
                "asked_at": found_question["asked_at"],
                "answered_at": found_question["answered_at"]
            })

            logger.info(f"接收用户回答: {question_id}, 回答: {answer[:50]}...")

            return {
                "success": True,
                "question_id": question_id,
                "answer": answer,
                "answered_at": found_question["answered_at"],
                "message": "回答已接收"
            }

        except Exception as e:
            logger.error(f"接收回答异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "接收回答异常"
            }

    async def inquire_requirements(
        self,
        user_id: str,
        task_id: str,
        requirements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        询问编纂需求

        Args:
            user_id: 用户ID
            task_id: 任务ID
            requirements: 需求列表

        Returns:
            询问结果
        """
        try:
            results = []

            for req in requirements:
                result = await self.ask_question(
                    user_id=user_id,
                    task_id=task_id,
                    question=req["question"],
                    question_type=req.get("type", "text"),
                    options=req.get("options"),
                    required=req.get("required", True)
                )

                if result["success"]:
                    results.append({
                        "requirement_name": req["name"],
                        "question_id": result["question_id"],
                        "status": "pending"
                    })
                else:
                    results.append({
                        "requirement_name": req["name"],
                        "status": "failed",
                        "error": result.get("error")
                    })

            logger.info(f"询问编纂需求: {user_id}, 问题数: {len(requirements)}")

            return {
                "success": True,
                "task_id": task_id,
                "requirements": results,
                "total_questions": len(requirements),
                "message": f"已发送 {len(requirements)} 个需求问题"
            }

        except Exception as e:
            logger.error(f"询问需求异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "询问需求异常"
            }

    async def get_question_history(
        self,
        task_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取问题历史

        Args:
            task_id: 任务ID
            user_id: 用户ID

        Returns:
            问题历史
        """
        try:
            history = self.question_history.get(task_id, [])

            # 如果指定了用户ID，过滤该用户的问题
            if user_id:
                # 在实际应用中应该有更精确的过滤
                pass

            logger.info(f"获取问题历史: {task_id}, 记录数: {len(history)}")

            return {
                "success": True,
                "task_id": task_id,
                "history": history,
                "total": len(history),
                "message": f"找到 {len(history)} 条历史记录"
            }

        except Exception as e:
            logger.error(f"获取历史异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "获取历史异常"
            }

    async def get_pending_questions(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        获取用户的待回答问题

        Args:
            user_id: 用户ID

        Returns:
            待回答问题列表
        """
        try:
            pending = []

            for task_id, questions in self.pending_questions.items():
                for q in questions:
                    if q["status"] == "pending":
                        # 在实际应用中应该检查user_id匹配
                        pending.append(q)

            logger.info(f"获取待回答问题: {user_id}, 数量: {len(pending)}")

            return {
                "success": True,
                "user_id": user_id,
                "pending_questions": pending,
                "total": len(pending),
                "message": f"找到 {len(pending)} 个待回答问题"
            }

        except Exception as e:
            logger.error(f"获取待回答问题异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "获取待回答问题异常"
            }

    async def send_notification(
        self,
        user_id: str,
        notification_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        发送通知

        Args:
            user_id: 用户ID
            notification_type: 通知类型（info/warning/error/success）
            message: 通知消息
            data: 附加数据

        Returns:
            发送结果
        """
        try:
            notification = {
                "notification_id": f"n_{datetime.now().timestamp()}",
                "user_id": user_id,
                "type": notification_type,
                "message": message,
                "data": data,
                "created_at": datetime.now().isoformat(),
                "read": False
            }

            # 保存到用户会话
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = {
                    "user_id": user_id,
                    "created_at": datetime.now().isoformat(),
                    "questions": [],
                    "notifications": []
                }

            if "notifications" not in self.user_sessions[user_id]:
                self.user_sessions[user_id]["notifications"] = []

            self.user_sessions[user_id]["notifications"].append(notification)

            logger.info(f"发送通知: {user_id}, 类型: {notification_type}, 消息: {message[:50]}...")

            return {
                "success": True,
                "notification_id": notification["notification_id"],
                "message": "通知已发送"
            }

        except Exception as e:
            logger.error(f"发送通知异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "发送通知异常"
            }


# 全局用户交互工具实例
_user_interaction_tool: Optional[UserInteractionTool] = None


def get_user_interaction_tool() -> UserInteractionTool:
    """获取用户交互工具单例"""
    global _user_interaction_tool
    if _user_interaction_tool is None:
        _user_interaction_tool = UserInteractionTool()
    return _user_interaction_tool
