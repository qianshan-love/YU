"""
HTTP客户端工具
用于调用大模型API
"""
import httpx
import asyncio
from typing import Dict, Any, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """大模型API客户端"""

    def __init__(self):
        self.base_url = settings.MODEL_BASE_URL
        self.model_name = settings.MODEL_NAME
        self.timeout = settings.MODEL_TIMEOUT
        self.client = httpx.AsyncClient(timeout=self.timeout)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        调用大模型Chat Completion API

        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数

        Returns:
            API响应结果
        """
        try:
            url = f"{self.base_url}/chat/completions"

            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature or settings.MODEL_TEMPERATURE,
                "max_tokens": max_tokens or settings.MODEL_MAX_TOKENS,
                **kwargs
            }

            logger.debug(f"调用LLM API: {url}")
            logger.debug(f"Payload: {payload}")

            response = await self.client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            response.raise_for_status()

            result = response.json()

            # 提取生成的文本
            if "choices" in result and len(result["choices"]) > 0:
                generated_text = result["choices"][0]["message"]["content"]
                logger.debug(f"LLM响应: {generated_text[:200]}...")

                return {
                    "success": True,
                    "content": generated_text,
                    "usage": result.get("usage", {}),
                    "model": result.get("model", self.model_name)
                }
            else:
                logger.warning(f"LLM API返回格式异常: {result}")
                return {
                    "success": False,
                    "error": "Invalid response format",
                    "raw_response": result
                }

        except httpx.TimeoutException:
            logger.error(f"LLM API调用超时")
            return {
                "success": False,
                "error": "Request timeout"
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"LLM API调用失败: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": f"HTTP error: {e.response.status_code}"
            }
        except Exception as e:
            logger.error(f"LLM API调用异常: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        生成文本（简化接口）

        Args:
            prompt: 用户提示
            system_prompt: 系统提示（可选）
            **kwargs: 其他参数

        Returns:
            生成的文本
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        result = await self.chat_completion(messages, **kwargs)

        if result.get("success"):
            return result.get("content", "")
        else:
            logger.error(f"生成文本失败: {result.get('error')}")
            return ""

    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


# 全局LLM客户端实例
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """获取LLM客户端单例"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
