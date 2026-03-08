"""
网络搜索工具
用于互联网检索资料
支持 seesea（国内搜索引擎）、Bing、Google
"""
from typing import Dict, Any, List, Optional
import logging
import asyncio
import httpx
from urllib.parse import quote
import os

# 尝试导入 seesea（延迟导入以避免初始化时的权限错误）
SEASEA_AVAILABLE = False
SeeseaSearcher = None
_seesea_import_attempted = False

def _can_use_seesea():
    """检查是否应该使用seasea"""
    import os
    return os.getenv("USE_SEASEA", "false").lower() == "true"

def _import_seesea():
    """延迟导入 seesea，避免初始化时的权限问题"""
    global SEASEA_AVAILABLE, SeeseaSearcher, _seesea_import_attempted
    if SEASEA_AVAILABLE:
        return True
    if _seesea_import_attempted:
        return SEASEA_AVAILABLE

    _seesea_import_attempted = True

    try:
        from seesea import Searcher as SeeseaSearcher
        SEASEA_AVAILABLE = True
        return True
    except (ImportError, Exception, BaseException) as e:
        print(f"警告: seesea 导入失败: {str(e)}，将使用其他搜索方式")
        SEASEA_AVAILABLE = False
        SeeseaSearcher = None
        return False

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class WebSearchTool:
    """网络搜索工具"""

    def __init__(self):
        """初始化网络搜索工具"""
        self.timeout = 30  # 30秒超时

        # seesea 配置（国内搜索引擎）
        self.use_seesea = _can_use_seesea()
        self.seesea_default_engine = os.getenv("SEASEA_DEFAULT_ENGINE", "bing")  # baidu/bing/360/so/sogou
        self.seesea_region = os.getenv("SEASEA_REGION", "china")  # china/international

        # 初始化 seesea searcher（延迟导入以避免权限问题）
        if self.use_seesea:
            if _import_seesea():
                try:
                    self.seesea_searcher = SeeseaSearcher(region=self.seesea_region)
                    logger.info(f"seesea搜索引擎初始化完成，区域: {self.seesea_region}, 默认引擎: {self.seesea_default_engine}")
                except Exception as e:
                    logger.warning(f"seesea初始化失败: {str(e)}，将降级到其他搜索方式")
                    self.seesea_searcher = None
                    self.use_seesea = False
            else:
                self.seesea_searcher = None
        else:
            self.seesea_searcher = None

        # API密钥配置（从环境变量读取）
        self.bing_api_key = os.getenv("BING_API_KEY", "")
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.google_search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")

        # 模拟搜索结果（作为后备）
        self.mock_search_results = {
            "示例县": {
                "title": "示例县简介",
                "url": "https://example.com/county",
                "snippet": "示例县位于某省中部，总面积1234平方公里，总人口56万人，历史悠久，经济发达。",
                "source": "示例县政府官网"
            },
            "地方志编纂": {
                "title": "地方志编纂工作指南",
                "url": "https://example.com/guide",
                "snippet": "地方志编纂要坚持实事求是原则，确保史料真实可靠，内容系统完整。",
                "source": "地方志工作办公室"
            },
            "县志体例": {
                "title": "县志体例规范",
                "url": "https://example.com/style",
                "snippet": "县志体例包括概述、建置区划、自然环境、人口、经济、政治、文化、社会、人物、大事记等部分。",
                "source": "地方志编纂规范"
            },
            "经济发展": {
                "title": "示例县经济发展情况",
                "url": "https://example.com/economy",
                "snippet": "2024年，示例县地区生产总值达到210亿元，同比增长7.7%，财政收入31亿元，增长10.7%。",
                "source": "示例县统计局"
            },
            "人口统计": {
                "title": "示例县人口统计数据",
                "url": "https://example.com/population",
                "snippet": "截至2024年底，示例县总人口58万人，城镇化率68%，常住人口55万人。",
                "source": "示例县统计局"
            }
        }

        # 检查可用搜索方式
        self.available_search_methods = []
        if self.seesea_searcher is not None:
            self.available_search_methods.append("seesea")
            logger.info("✓ seasea搜索引擎可用")
        if self.bing_api_key:
            self.available_search_methods.append("bing")
            logger.info("✓ Bing API可用")
        if self.google_api_key and self.google_search_engine_id:
            self.available_search_methods.append("google")
            logger.info("✓ Google API可用")
        self.available_search_methods.append("mock")
        logger.info("✓ 模拟搜索可用")

        if not self.available_search_methods:
            logger.warning("未配置任何搜索方式，将使用模拟数据")

        logger.info("网络搜索工具初始化完成")

    async def search(
        self,
        query: str,
        num_results: int = 5,
        source: str = "auto"
    ) -> Dict[str, Any]:
        """
        网络搜索

        Args:
            query: 搜索关键词
            num_results: 返回结果数量
            source: 数据源（auto/seesea/bing/google/mock）

        Returns:
            搜索结果
        """
        logger.info(f"网络搜索: {query}, 数据源: {source}")

        try:
            # 决定使用哪个搜索源
            actual_source = source

            if source == "auto":
                # 自动选择：优先 seesea > bing > google > mock
                if "seesea" in self.available_search_methods:
                    actual_source = "seesea"
                elif "bing" in self.available_search_methods:
                    actual_source = "bing"
                elif "google" in self.available_search_methods:
                    actual_source = "google"
                else:
                    actual_source = "mock"

            # 执行搜索
            if actual_source == "seesea":
                # 使用 seesea 搜索
                results = await self._seesea_search(query, num_results)
            elif actual_source == "mock":
                # 使用模拟数据
                results = await self._mock_search(query, num_results)
            elif actual_source == "bing":
                # 使用 Bing API
                results = await self._bing_search(query, num_results)
            elif actual_source == "google":
                # 使用 Google API
                results = await self._google_search(query, num_results)
            elif actual_source == "custom":
                # 使用自定义搜索（待实现）
                results = await self._custom_search(query, num_results)
            else:
                # 默认使用 seesea（如果可用）或模拟数据
                if "seesea" in self.available_search_methods:
                    results = await self._seesea_search(query, num_results)
                else:
                    results = await self._mock_search(query, num_results)

            return {
                "success": True,
                "message": f"搜索完成，找到{len(results)}条结果",
                "data": {
                    "query": query,
                    "results": results,
                    "total": len(results),
                    "source": actual_source
                }
            }

        except Exception as e:
            logger.error(f"网络搜索异常: {str(e)}")
            # 如果真实搜索失败，降级到模拟数据
            if source in ["seesea", "bing", "google"]:
                logger.info("真实搜索失败，降级到模拟数据")
                try:
                    results = await self._mock_search(query, num_results)
                    return {
                        "success": True,
                        "message": f"搜索完成（降级到模拟），找到{len(results)}条结果",
                        "data": {
                            "query": query,
                            "results": results,
                            "total": len(results),
                            "source": "mock"
                        }
                    }
                except:
                    pass

            return {
                "success": False,
                "message": f"搜索异常: {str(e)}",
                "data": {
                    "query": query,
                    "results": [],
                    "total": 0,
                    "source": source
                }
            }

    async def _mock_search(
        self,
        query: str,
        num_results: int
    ) -> List[Dict[str, Any]]:
        """
        模拟搜索

        Args:
            query: 搜索关键词
            num_results: 返回结果数量

        Returns:
            搜索结果列表
        """
        results = []

        # 简单的关键词匹配
        for key, value in self.mock_search_results.items():
            if query.lower() in key.lower():
                results.append({
                    "title": value["title"],
                    "url": value["url"],
                    "snippet": value["snippet"],
                    "source": value["source"]
                })

            if len(results) >= num_results:
                break

        # 如果没有找到精确匹配，尝试模糊匹配
        if len(results) < num_results:
            for key, value in self.mock_search_results.items():
                # 检查是否包含查询词的任意字符
                if any(char in key.lower() for char in query.lower()):
                    # 避免重复
                    if not any(r["url"] == value["url"] for r in results):
                        results.append({
                            "title": value["title"],
                            "url": value["url"],
                            "snippet": value["snippet"],
                            "source": value["source"]
                        })

                    if len(results) >= num_results:
                        break

        return results

    async def _seesea_search(
        self,
        query: str,
        num_results: int,
        engine: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        seesea搜索（支持国内搜索引擎）

        Args:
            query: 搜索关键词
            num_results: 返回结果数量
            engine: 搜索引擎（baidu/bing/360/so/sogou/默认）

        Returns:
            搜索结果列表
        """
        # 确保seesea已导入
        use_seesea = getattr(self, 'use_seesea', False)
        if self.seesea_searcher is None and use_seesea:
            _import_seesea()
            if SEASEA_AVAILABLE:
                try:
                    self.seesea_searcher = SeeseaSearcher(region=self.seesea_region)
                except Exception as e:
                    logger.warning(f"seesea初始化失败: {str(e)}")
                    self.seesea_searcher = None

        if self.seesea_searcher is None:
            logger.warning("seesea未安装或初始化失败，使用模拟数据")
            return await self._mock_search(query, num_results)

        # 确定使用的搜索引擎
        search_engine = engine or self.seesea_default_engine

        try:
            # seesea的search方法是同步的，需要在事件循环中运行
            loop = asyncio.get_event_loop()
            search_results = await loop.run_in_executor(
                None,
                self.seesea_searcher.search,
                query,
                search_engine
            )

            if not search_results:
                logger.warning(f"seasea搜索无结果: {query}")
                return []

            # 转换为标准格式
            results = []
            for item in search_results[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("description", ""),
                    "source": f"seasea_{search_engine}"
                })

            logger.info(f"seasea搜索成功: {query}, 引擎: {search_engine}, 结果数: {len(results)}")
            return results

        except Exception as e:
            logger.error(f"seasea搜索异常: {str(e)}")
            # 降级到模拟数据
            return await self._mock_search(query, num_results)

    async def _bing_search(
        self,
        query: str,
        num_results: int
    ) -> List[Dict[str, Any]]:
        """
        Bing搜索

        Args:
            query: 搜索关键词
            num_results: 返回结果数量

        Returns:
            搜索结果列表
        """
        if not self.bing_api_key:
            logger.warning("Bing API Key未配置，使用模拟数据")
            return await self._mock_search(query, num_results)

        endpoint = "https://api.bing.microsoft.com/v7.0/search"

        headers = {
            "Ocp-Apim-Subscription-Key": self.bing_api_key
        }

        params = {
            "q": query,
            "count": min(num_results, 50),  # Bing限制最大50
            "offset": 0,
            "mkt": "zh-CN"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()

                results = []
                for item in data.get("webPages", {}).get("value", []):
                    results.append({
                        "title": item["name"],
                        "url": item["url"],
                        "snippet": item["snippet"],
                        "source": "Bing"
                    })

                logger.info(f"Bing搜索成功，找到{len(results)}条结果")
                return results

        except httpx.HTTPStatusError as e:
            logger.error(f"Bing API错误: {e.response.status_code} - {e.response.text}")
            # 降级到模拟数据
            return await self._mock_search(query, num_results)
        except Exception as e:
            logger.error(f"Bing搜索异常: {str(e)}")
            # 降级到模拟数据
            return await self._mock_search(query, num_results)

    async def _google_search(
        self,
        query: str,
        num_results: int
    ) -> List[Dict[str, Any]]:
        """
        Google搜索（需要配置API Key和Search Engine ID）

        Args:
            query: 搜索关键词
            num_results: 返回结果数量

        Returns:
            搜索结果列表
        """
        if not self.google_api_key or not self.google_search_engine_id:
            logger.warning("Google API配置不完整，使用模拟数据")
            return await self._mock_search(query, num_results)

        endpoint = "https://www.googleapis.com/customsearch/v1"

        params = {
            "key": self.google_api_key,
            "cx": self.google_search_engine_id,
            "q": query,
            "num": min(num_results, 10)  # Google限制最大10
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                data = response.json()

                results = []
                for item in data.get("items", []):
                    results.append({
                        "title": item["title"],
                        "url": item["link"],
                        "snippet": item.get("snippet", ""),
                        "source": "Google"
                    })

                logger.info(f"Google搜索成功，找到{len(results)}条结果")
                return results

        except httpx.HTTPStatusError as e:
            logger.error(f"Google API错误: {e.response.status_code} - {e.response.text}")
            # 降级到模拟数据
            return await self._mock_search(query, num_results)
        except Exception as e:
            logger.error(f"Google搜索异常: {str(e)}")
            # 降级到模拟数据
            return await self._mock_search(query, num_results)

    async def _custom_search(
        self,
        query: str,
        num_results: int
    ) -> List[Dict[str, Any]]:
        """
        自定义搜索（待实现，可以接入其他搜索API）

        Args:
            query: 搜索关键词
            num_results: 返回结果数量

        Returns:
            搜索结果列表
        """
        # 暂时降级到模拟数据
        logger.info("自定义搜索未实现，使用模拟数据")
        return await self._mock_search(query, num_results)

    async def fetch_page(
        self,
        url: str,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取网页内容

        Args:
            url: 网页URL
            timeout: 超时时间（秒）

        Returns:
            网页内容
        """
        logger.info(f"获取网页内容: {url}")

        try:
            timeout = timeout or self.timeout

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                response.raise_for_status()

                # 简化处理：直接返回文本内容
                # 实际应用中可能需要解析HTML

                return {
                    "success": True,
                    "message": "获取成功",
                    "data": {
                        "url": url,
                        "content": response.text[:10000],  # 限制内容长度
                        "status_code": response.status_code
                    }
                }

        except httpx.TimeoutException:
            logger.error(f"获取网页超时: {url}")
            return {
                "success": False,
                "message": "请求超时",
                "data": {}
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"获取网页失败: {url}, 状态码: {e.response.status_code}")
            return {
                "success": False,
                "message": f"HTTP错误: {e.response.status_code}",
                "data": {}
            }
        except Exception as e:
            logger.error(f"获取网页异常: {str(e)}")
            return {
                "success": False,
                "message": f"获取异常: {str(e)}",
                "data": {}
            }

    async def batch_search(
        self,
        queries: List[str],
        num_results: int = 5
    ) -> Dict[str, Any]:
        """
        批量搜索

        Args:
            queries: 搜索关键词列表
            num_results: 每个查询返回结果数量

        Returns:
            搜索结果
        """
        logger.info(f"批量搜索: {len(queries)}个查询")

        try:
            # 并行搜索
            search_tasks = [
                self.search(query, num_results)
                for query in queries
            ]

            results = await asyncio.gather(*search_tasks, return_exceptions=True)

            # 合并结果
            all_results = {}
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"搜索异常: {queries[i]}, 错误: {str(result)}")
                    all_results[queries[i]] = {
                        "success": False,
                        "message": str(result),
                        "data": {}
                    }
                else:
                    all_results[queries[i]] = result

            return {
                "success": True,
                "message": f"批量搜索完成",
                "data": {
                    "queries": queries,
                    "results": all_results,
                    "total_queries": len(queries)
                }
            }

        except Exception as e:
            logger.error(f"批量搜索异常: {str(e)}")
            return {
                "success": False,
                "message": f"批量搜索异常: {str(e)}",
                "data": {}
            }

    async def search_with_context(
        self,
        query: str,
        context: str,
        num_results: int = 5
    ) -> Dict[str, Any]:
        """
        带上下文搜索

        Args:
            query: 搜索关键词
            context: 上下文信息
            num_results: 返回结果数量

        Returns:
            搜索结果
        """
        logger.info(f"带上下文搜索: {query}")

        # 将上下文信息加入到搜索查询中
        enhanced_query = f"{context} {query}"

        return await self.search(enhanced_query, num_results)


# 全局网络搜索工具实例
_web_search_tool: Optional[WebSearchTool] = None


def get_web_search_tool() -> WebSearchTool:
    """获取网络搜索工具单例"""
    global _web_search_tool
    if _web_search_tool is None:
        _web_search_tool = WebSearchTool()
    return _web_search_tool
