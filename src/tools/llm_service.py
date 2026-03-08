"""
大模型服务
封装LLM调用接口，为所有Agent提供统一的模型调用能力
"""
from typing import Dict, Any, List, Optional
import httpx
import json
import logging
import asyncio

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class LLMService:
    """大模型服务类"""

    def __init__(self):
        """初始化LLM服务"""
        self.api_url = "http://140.143.163.123:59655/v1/chat/completions"
        self.model_name = "Qwen3.5-35B-A3B-UD-Q4_K_XL"
        self.timeout = 60  # 60秒超时
        self.temperature = 0.7
        self.max_tokens = 1024

        logger.info(f"大模型服务初始化完成，模型: {self.model_name}")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        调用大模型进行对话

        Args:
            messages: 消息列表，格式 [{"role": "user", "content": "..."}]
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成token数
            stream: 是否流式输出

        Returns:
            模型响应结果
        """
        try:
            # 准备请求数据
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature if temperature is not None else self.temperature,
                "max_tokens": max_tokens if max_tokens is not None else self.max_tokens,
                "stream": stream
            }

            logger.info(f"调用大模型，消息数: {len(messages)}, 总token数: {sum(len(m.get('content', '')) for m in messages)}")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()

                result = response.json()

                # 提取响应内容
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0].get("message", {}).get("content", "")
                    usage = result.get("usage", {})

                    logger.info(f"大模型调用成功，输出长度: {len(content)}, 用量: {usage}")

                    return {
                        "success": True,
                        "content": content,
                        "usage": usage,
                        "model": result.get("model", self.model_name),
                        "finish_reason": result["choices"][0].get("finish_reason", "stop")
                    }
                else:
                    logger.warning(f"大模型响应格式异常: {result}")
                    return {
                        "success": False,
                        "error": "响应格式异常",
                        "raw_response": result
                    }

        except httpx.HTTPStatusError as e:
            logger.error(f"大模型HTTP错误: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": f"HTTP错误: {e.response.status_code}",
                "message": str(e)
            }
        except httpx.TimeoutException:
            logger.error("大模型调用超时")
            return {
                "success": False,
                "error": "请求超时",
                "message": "模型响应超时，请稍后重试"
            }
        except Exception as e:
            logger.error(f"大模型调用异常: {str(e)}")
            return {
                "success": False,
                "error": "调用异常",
                "message": str(e)
            }

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        生成文本

        Args:
            prompt: 提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大生成token数

        Returns:
            生成结果
        """
        messages = []

        # 添加系统提示词
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        # 添加用户提示词
        messages.append({
            "role": "user",
            "content": prompt
        })

        return await self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

    async def generate_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成文本（带工具调用支持）

        Args:
            messages: 消息列表
            tools: 工具定义列表
            tool_choice: 工具选择策略

        Returns:
            生成结果，可能包含工具调用
        """
        try:
            # 准备请求数据
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }

            # 添加工具支持
            if tools:
                payload["tools"] = tools
                logger.info(f"启用工具调用支持，工具数: {len(tools)}")

            if tool_choice:
                payload["tool_choice"] = tool_choice

            logger.info(f"调用大模型（工具模式），消息数: {len(messages)}")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()

                result = response.json()

                # 提取响应内容
                if "choices" in result and len(result["choices"]) > 0:
                    choice = result["choices"][0]
                    message = choice.get("message", {})

                    content = message.get("content", "")
                    tool_calls = message.get("tool_calls", [])

                    logger.info(f"大模型调用成功，工具调用数: {len(tool_calls)}")

                    return {
                        "success": True,
                        "content": content,
                        "tool_calls": tool_calls,
                        "usage": result.get("usage", {}),
                        "model": result.get("model", self.model_name)
                    }
                else:
                    logger.warning(f"大模型响应格式异常: {result}")
                    return {
                        "success": False,
                        "error": "响应格式异常",
                        "raw_response": result
                    }

        except Exception as e:
            logger.error(f"大模型工具调用异常: {str(e)}")
            return {
                "success": False,
                "error": "调用异常",
                "message": str(e)
            }

    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None
    ):
        """
        流式对话

        Args:
            messages: 消息列表
            temperature: 温度参数

        Yields:
            流式响应内容
        """
        try:
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature if temperature is not None else self.temperature,
                "max_tokens": self.max_tokens,
                "stream": True
            }

            logger.info(f"开始流式对话，消息数: {len(messages)}")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    self.api_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            logger.error(f"流式对话异常: {str(e)}")
            yield f"错误: {str(e)}"


# 全局LLM服务实例
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """获取LLM服务单例"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


# 便捷函数
async def call_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> str:
    """
    便捷的LLM调用函数

    Args:
        prompt: 提示词
        system_prompt: 系统提示词
        temperature: 温度参数
        max_tokens: 最大生成token数

    Returns:
        生成的文本内容
    """
    service = get_llm_service()
    result = await service.generate_text(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens
    )

    if result["success"]:
        return result["content"]
    else:
        logger.error(f"LLM调用失败: {result.get('error')}")
        return f"调用失败: {result.get('message', '未知错误')}"


async def chat_llm(
    messages: List[Dict[str, str]],
    temperature: Optional[float] = None
) -> str:
    """
    便捷的LLM对话函数

    Args:
        messages: 消息列表
        temperature: 温度参数

    Returns:
        模型响应内容
    """
    service = get_llm_service()
    result = await service.chat(
        messages=messages,
        temperature=temperature
    )

    if result["success"]:
        return result["content"]
    else:
        logger.error(f"LLM对话失败: {result.get('error')}")
        return f"调用失败: {result.get('message', '未知错误')}"
