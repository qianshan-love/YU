"""
知识检索工具
用于检索知识库、旧志、年鉴等资料
"""
from typing import Dict, Any, List, Optional
import logging
import asyncio
from datetime import datetime

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class RetrievalTool:
    """知识检索工具"""

    def __init__(self):
        """初始化知识检索工具"""
        # 模拟知识库数据
        self.knowledge_base = self._init_knowledge_base()
        self.old_annals = self._init_old_annals()
        self.yearbooks = self._init_yearbooks()

        logger.info("知识检索工具初始化完成")

    def _init_knowledge_base(self) -> Dict[str, Any]:
        """
        初始化知识库

        Returns:
            知识库数据
        """
        return {
            "县志编纂知识": {
                "编纂原则": {
                    "指导思想": "坚持马克思主义，坚持社会主义方向",
                    "基本原则": "实事求是，存真求实",
                    "质量标准": "政治方向正确，史料真实可靠，内容系统完整"
                },
                "编纂流程": {
                    "筹备阶段": "成立编纂委员会，制定编纂方案",
                    "资料收集": "广泛收集各类资料，建立资料库",
                    "初稿撰写": "按照目录分工，逐章逐节撰写",
                    "审核修改": "多方审核，反复修改完善",
                    "终稿审定": "编纂委员会审定，报上级部门批准"
                }
            },
            "地方志知识": {
                "基本概念": {
                    "地方志": "记述一定区域自然、经济、政治、文化、社会等各方面历史和现状的综合性资料性文献",
                    "志书": "地方志的简称，是地方志的主体",
                    "年鉴": "逐年编纂的综合性资料工具书",
                    "方志": "地方志的统称"
                },
                "地方志类型": {
                    "综合志": "记述一地全面情况的志书",
                    "专业志": "记述某一方面情况的志书",
                    "部门志": "记述某一部门情况的志书",
                    "乡镇志": "记述乡镇情况的志书"
                }
            }
        }

    def _init_old_annals(self) -> Dict[str, Any]:
        """
        初始化旧志库

        Returns:
            旧志数据
        """
        return {
            "示例县志": {
                "概述": "示例县位于某省中部，总面积1234平方公里，总人口56万人",
                "历史沿革": "示例县历史悠久，西汉建县，距今已有两千多年历史",
                "地理位置": "地处东经120°-121°，北纬30°-31°，属于亚热带季风气候",
                "行政区划": "现辖10个镇，5个乡，3个街道办事处"
            },
            "旧志资料": {
                "建置沿革": "西汉元封二年（前109年）置县，属某郡",
                "历代变迁": "历经汉、晋、南北朝、隋、唐、宋、元、明、清等朝代",
                "县名由来": "因地处某山之南，某水之北，故得名"
            }
        }

    def _init_yearbooks(self) -> Dict[str, Any]:
        """
        初始化年鉴库

        Returns:
            年鉴数据
        """
        return {
            "2020年": {
                "经济发展": {
                    "地区生产总值": "150亿元，增长6.5%",
                    "财政收入": "20亿元，增长8.2%",
                    "固定资产投资": "100亿元，增长10%"
                },
                "社会发展": {
                    "人口": "56万人，城镇化率60%",
                    "教育": "拥有中小学50所，在校学生5万人",
                    "医疗": "拥有医院15所，床位2000张"
                }
            },
            "2021年": {
                "经济发展": {
                    "地区生产总值": "165亿元，增长10%",
                    "财政收入": "22亿元，增长10%",
                    "固定资产投资": "110亿元，增长10%"
                },
                "社会发展": {
                    "人口": "56.5万人，城镇化率62%",
                    "教育": "拥有中小学52所，在校学生5.2万人",
                    "医疗": "拥有医院16所，床位2200张"
                }
            },
            "2022年": {
                "经济发展": {
                    "地区生产总值": "180亿元，增长9%",
                    "财政收入": "25亿元，增长13.6%",
                    "固定资产投资": "120亿元，增长9%"
                },
                "社会发展": {
                    "人口": "57万人，城镇化率64%",
                    "教育": "拥有中小学55所，在校学生5.5万人",
                    "医疗": "拥有医院18所，床位2500张"
                }
            },
            "2023年": {
                "经济发展": {
                    "地区生产总值": "195亿元，增长8.3%",
                    "财政收入": "28亿元，增长12%",
                    "固定资产投资": "130亿元，增长8.3%"
                },
                "社会发展": {
                    "人口": "57.5万人，城镇化率66%",
                    "教育": "拥有中小学58所，在校学生5.8万人",
                    "医疗": "拥有医院20所，床位2800张"
                }
            },
            "2024年": {
                "经济发展": {
                    "地区生产总值": "210亿元，增长7.7%",
                    "财政收入": "31亿元，增长10.7%",
                    "固定资产投资": "140亿元，增长7.7%"
                },
                "社会发展": {
                    "人口": "58万人，城镇化率68%",
                    "教育": "拥有中小学60所，在校学生6万人",
                    "医疗": "拥有医院22所，床位3000张"
                }
            }
        }

    async def search_knowledge_base(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        搜索知识库

        Args:
            query: 查询关键词
            category: 类别（可选）
            limit: 返回结果数量限制

        Returns:
            搜索结果
        """
        logger.info(f"搜索知识库: {query}")

        try:
            results = []

            # 简化的关键词匹配搜索
            for kb_name, kb_content in self.knowledge_base.items():
                if category and kb_name != category:
                    continue

                # 递归搜索
                matches = self._search_dict(kb_content, query)

                for match in matches:
                    results.append({
                        "source": kb_name,
                        "content": match,
                        "relevance": self._calculate_relevance(match, query)
                    })

                    if len(results) >= limit:
                        break

                if len(results) >= limit:
                    break

            # 按相关性排序
            results.sort(key=lambda x: x["relevance"], reverse=True)

            return {
                "success": True,
                "message": f"搜索完成，找到{len(results)}条结果",
                "data": {
                    "query": query,
                    "results": results,
                    "total": len(results)
                }
            }

        except Exception as e:
            logger.error(f"搜索知识库异常: {str(e)}")
            return {
                "success": False,
                "message": f"搜索异常: {str(e)}",
                "data": {
                    "query": query,
                    "results": [],
                    "total": 0
                }
            }

    async def search_old_annals(
        self,
        query: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        检索旧志

        Args:
            query: 查询关键词
            limit: 返回结果数量限制

        Returns:
            检索结果
        """
        logger.info(f"检索旧志: {query}")

        try:
            results = []

            # 搜索旧志库
            for annal_name, annal_content in self.old_annals.items():
                matches = self._search_dict(annal_content, query)

                for match in matches:
                    results.append({
                        "source": annal_name,
                        "content": match,
                        "relevance": self._calculate_relevance(match, query)
                    })

                    if len(results) >= limit:
                        break

                if len(results) >= limit:
                    break

            # 按相关性排序
            results.sort(key=lambda x: x["relevance"], reverse=True)

            return {
                "success": True,
                "message": f"检索完成，找到{len(results)}条结果",
                "data": {
                    "query": query,
                    "results": results,
                    "total": len(results)
                }
            }

        except Exception as e:
            logger.error(f"检索旧志异常: {str(e)}")
            return {
                "success": False,
                "message": f"检索异常: {str(e)}",
                "data": {
                    "query": query,
                    "results": [],
                    "total": 0
                }
            }

    async def search_yearbook(
        self,
        query: str,
        year: Optional[str] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        检索年鉴

        Args:
            query: 查询关键词
            year: 年份（可选）
            limit: 返回结果数量限制

        Returns:
            检索结果
        """
        logger.info(f"检索年鉴: {query}, 年份: {year}")

        try:
            results = []

            # 如果指定了年份，只搜索该年份
            if year:
                yearbooks_to_search = {year: self.yearbooks.get(year)}
            else:
                yearbooks_to_search = self.yearbooks

            # 搜索年鉴
            for year_name, year_content in yearbooks_to_search.items():
                if year_content is None:
                    continue

                matches = self._search_dict(year_content, query)

                for match in matches:
                    results.append({
                        "source": f"{year_name}年鉴",
                        "content": match,
                        "relevance": self._calculate_relevance(match, query)
                    })

                    if len(results) >= limit:
                        break

                if len(results) >= limit:
                    break

            # 按相关性排序
            results.sort(key=lambda x: x["relevance"], reverse=True)

            return {
                "success": True,
                "message": f"检索完成，找到{len(results)}条结果",
                "data": {
                    "query": query,
                    "year": year,
                    "results": results,
                    "total": len(results)
                }
            }

        except Exception as e:
            logger.error(f"检索年鉴异常: {str(e)}")
            return {
                "success": False,
                "message": f"检索异常: {str(e)}",
                "data": {
                    "query": query,
                    "year": year,
                    "results": [],
                    "total": 0
                }
            }

    async def comprehensive_search(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        综合搜索

        Args:
            query: 查询关键词
            sources: 数据源列表（knowledge_base/old_annals/yearbook）
            limit: 返回结果数量限制

        Returns:
            搜索结果
        """
        logger.info(f"综合搜索: {query}, 数据源: {sources}")

        if sources is None:
            sources = ["knowledge_base", "old_annals", "yearbook"]

        all_results = []

        # 并行搜索各个数据源
        search_tasks = []

        if "knowledge_base" in sources:
            search_tasks.append(self.search_knowledge_base(query, limit=limit))

        if "old_annals" in sources:
            search_tasks.append(self.search_old_annals(query, limit=limit))

        if "yearbook" in sources:
            search_tasks.append(self.search_yearbook(query, limit=limit))

        # 执行搜索
        results_list = await asyncio.gather(*search_tasks, return_exceptions=True)

        # 合并结果
        for result in results_list:
            if isinstance(result, Exception):
                logger.error(f"搜索异常: {str(result)}")
                continue

            if result["success"]:
                all_results.extend(result["data"]["results"])

        # 去重
        seen = set()
        unique_results = []
        for result in all_results:
            key = (result["source"], str(result["content"]))
            if key not in seen:
                seen.add(key)
                unique_results.append(result)

        # 按相关性排序
        unique_results.sort(key=lambda x: x["relevance"], reverse=True)

        # 限制返回数量
        unique_results = unique_results[:limit]

        return {
            "success": True,
            "message": f"综合搜索完成，找到{len(unique_results)}条结果",
            "data": {
                "query": query,
                "sources": sources,
                "results": unique_results,
                "total": len(unique_results)
            }
        }

    def _search_dict(
        self,
        data: Dict[str, Any],
        query: str,
        path: str = ""
    ) -> List[str]:
        """
        递归搜索字典

        Args:
            data: 字典数据
            query: 查询关键词
            path: 当前路径

        Returns:
            匹配结果列表
        """
        results = []
        query_lower = query.lower()

        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key

            if isinstance(value, dict):
                # 递归搜索
                results.extend(self._search_dict(value, query, current_path))

            elif isinstance(value, str):
                # 检查是否包含查询词
                if query_lower in value.lower():
                    results.append({
                        "key": current_path,
                        "value": value
                    })

            elif isinstance(value, (int, float)):
                # 数字转字符串后检查
                value_str = str(value)
                if query_lower in value_str.lower():
                    results.append({
                        "key": current_path,
                        "value": value_str
                    })

        return results

    def _calculate_relevance(self, match: Dict[str, Any], query: str) -> float:
        """
        计算相关性

        Args:
            match: 匹配结果
            query: 查询关键词

        Returns:
            相关性分数
        """
        if not isinstance(match, dict):
            return 0.0

        value = match.get("value", "")
        query_lower = query.lower()
        value_lower = value.lower()

        # 计算关键词出现次数
        count = value_lower.count(query_lower)

        # 计算关键词占比
        ratio = count / len(value_lower) if value_lower else 0

        # 基础分数
        score = count * 10 + ratio * 100

        # 如果完全匹配，提高分数
        if query_lower == value_lower.strip():
            score += 100

        return score

    async def get_yearbook_data(
        self,
        year: str,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取年鉴数据

        Args:
            year: 年份
            category: 类别（可选）

        Returns:
            年鉴数据
        """
        logger.info(f"获取年鉴数据: {year}, 类别: {category}")

        try:
            year_data = self.yearbooks.get(year)

            if year_data is None:
                return {
                    "success": False,
                    "message": f"不存在{year}年份数据",
                    "data": {}
                }

            if category:
                if category in year_data:
                    return {
                        "success": True,
                        "message": "获取成功",
                        "data": {
                            "year": year,
                            "category": category,
                            **year_data[category]
                        }
                    }
                else:
                    return {
                        "success": False,
                        "message": f"不存在{category}类别",
                        "data": {}
                    }

            return {
                "success": True,
                "message": "获取成功",
                "data": {
                    "year": year,
                    **year_data
                }
            }

        except Exception as e:
            logger.error(f"获取年鉴数据异常: {str(e)}")
            return {
                "success": False,
                "message": f"获取异常: {str(e)}",
                "data": {}
            }


# 全局知识检索工具实例
_retrieval_tool: Optional[RetrievalTool] = None


def get_retrieval_tool() -> RetrievalTool:
    """获取知识检索工具单例"""
    global _retrieval_tool
    if _retrieval_tool is None:
        _retrieval_tool = RetrievalTool()
    return _retrieval_tool
