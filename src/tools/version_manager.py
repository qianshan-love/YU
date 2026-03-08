"""
版本管理工具
负责版本生成、查询、对比、回退、归档等功能
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging

from src.utils.logger import setup_logger
from src.utils.helpers import generate_version_id

logger = setup_logger(__name__)


class VersionManager:
    """版本管理工具"""

    def __init__(self):
        """初始化版本管理工具"""
        # 内存存储（实际项目应使用数据库）
        self.versions = {}  # {chapter_id: [VersionInfo]}
        self.archived_versions = {}  # {task_id: VersionInfo}

        logger.info("版本管理工具初始化完成")

    async def create_version(
        self,
        chapter_id: str,
        content: str,
        created_by: str,
        version_type: str = "initial",
        parent_version_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建新版本

        Args:
            chapter_id: 章节ID
            content: 版本内容
            created_by: 创建者
            version_type: 版本类型（initial/revised/final）
            parent_version_id: 父版本ID

        Returns:
            创建结果
        """
        try:
            # 获取章节的版本列表
            chapter_versions = self.versions.get(chapter_id, [])

            # 生成版本号
            version_number = len(chapter_versions) + 1
            version_id = generate_version_id(chapter_id, version_number)

            # 计算与上一版本的差异
            diff = ""
            if chapter_versions:
                prev_version = chapter_versions[-1]
                diff = self._calculate_diff(prev_version["content"], content)

            # 创建版本信息
            version_info = {
                "version_id": version_id,
                "chapter_id": chapter_id,
                "version_number": version_number,
                "content": content,
                "created_by": created_by,
                "created_at": datetime.now().isoformat(),
                "version_type": version_type,
                "status": "active",
                "diff": diff,
                "parent_version_id": parent_version_id,
                "word_count": len(content),
                "line_count": len(content.split('\n'))
            }

            # 添加到版本列表
            chapter_versions.append(version_info)
            self.versions[chapter_id] = chapter_versions

            logger.info(f"创建版本成功: {version_id}, 章节: {chapter_id}, 版本号: {version_number}")

            return {
                "success": True,
                "version_id": version_id,
                "version_number": version_number,
                "chapter_id": chapter_id,
                "created_at": version_info["created_at"],
                "message": f"版本 {version_number} 创建成功"
            }

        except Exception as e:
            logger.error(f"创建版本异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "创建版本异常"
            }

    async def query_version(
        self,
        chapter_id: str,
        version_id: Optional[str] = None,
        version_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        查询版本

        Args:
            chapter_id: 章节ID
            version_id: 版本ID
            version_number: 版本号

        Returns:
            查询结果
        """
        try:
            chapter_versions = self.versions.get(chapter_id, [])

            if not chapter_versions:
                return {
                    "success": False,
                    "error": "章节不存在",
                    "message": f"章节 {chapter_id} 不存在"
                }

            # 根据version_id查询
            if version_id:
                for version in chapter_versions:
                    if version["version_id"] == version_id:
                        logger.info(f"查询版本成功: {version_id}")
                        return {
                            "success": True,
                            "version": version,
                            "message": "版本查询成功"
                        }
                return {
                    "success": False,
                    "error": "版本不存在",
                    "message": f"版本 {version_id} 不存在"
                }

            # 根据version_number查询
            elif version_number:
                for version in chapter_versions:
                    if version["version_number"] == version_number:
                        logger.info(f"查询版本成功: 章节{chapter_id}, 版本{version_number}")
                        return {
                            "success": True,
                            "version": version,
                            "message": "版本查询成功"
                        }
                return {
                    "success": False,
                    "error": "版本不存在",
                    "message": f"版本号 {version_number} 不存在"
                }

            # 返回最新版本
            else:
                latest_version = chapter_versions[-1]
                logger.info(f"查询最新版本: {latest_version['version_id']}")
                return {
                    "success": True,
                    "version": latest_version,
                    "message": "最新版本查询成功"
                }

        except Exception as e:
            logger.error(f"查询版本异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "查询版本异常"
            }

    async def list_versions(
        self,
        chapter_id: str,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        列出版本

        Args:
            chapter_id: 章节ID
            limit: 返回数量限制

        Returns:
            版本列表
        """
        try:
            chapter_versions = self.versions.get(chapter_id, [])

            if not chapter_versions:
                return {
                    "success": False,
                    "error": "章节不存在",
                    "message": f"章节 {chapter_id} 不存在"
                }

            # 按版本号排序（降序）
            sorted_versions = sorted(chapter_versions, key=lambda x: x["version_number"], reverse=True)

            # 应用数量限制
            if limit and limit > 0:
                sorted_versions = sorted_versions[:limit]

            logger.info(f"列出版本成功: {chapter_id}, 数量: {len(sorted_versions)}")

            return {
                "success": True,
                "versions": sorted_versions,
                "total": len(sorted_versions),
                "chapter_id": chapter_id,
                "message": f"找到 {len(sorted_versions)} 个版本"
            }

        except Exception as e:
            logger.error(f"列出版本异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "列出版本异常"
            }

    async def compare_versions(
        self,
        version_id_1: str,
        version_id_2: str
    ) -> Dict[str, Any]:
        """
        对比两个版本

        Args:
            version_id_1: 版本1 ID
            version_id_2: 版本2 ID

        Returns:
            对比结果
        """
        try:
            # 查找两个版本
            version_1 = self._find_version_by_id(version_id_1)
            version_2 = self._find_version_by_id(version_id_2)

            if not version_1 or not version_2:
                missing = []
                if not version_1:
                    missing.append(version_id_1)
                if not version_2:
                    missing.append(version_id_2)

                return {
                    "success": False,
                    "error": "版本不存在",
                    "message": f"版本 {', '.join(missing)} 不存在"
                }

            # 对比内容
            diff = self._calculate_diff(version_1["content"], version_2["content"])

            # 统计差异
            stats = {
                "version_1": {
                    "version_id": version_id_1,
                    "version_number": version_1["version_number"],
                    "word_count": version_1["word_count"],
                    "created_at": version_1["created_at"]
                },
                "version_2": {
                    "version_id": version_id_2,
                    "version_number": version_2["version_number"],
                    "word_count": version_2["word_count"],
                    "created_at": version_2["created_at"]
                },
                "differences": {
                    "word_count_change": version_2["word_count"] - version_1["word_count"],
                    "has_content_change": version_1["content"] != version_2["content"]
                }
            }

            logger.info(f"版本对比成功: {version_id_1} vs {version_id_2}")

            return {
                "success": True,
                "version_1": version_1,
                "version_2": version_2,
                "diff": diff,
                "stats": stats,
                "message": "版本对比成功"
            }

        except Exception as e:
            logger.error(f"版本对比异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "版本对比异常"
            }

    async def rollback_version(
        self,
        chapter_id: str,
        target_version_id: str
    ) -> Dict[str, Any]:
        """
        回退到指定版本

        Args:
            chapter_id: 章节ID
            target_version_id: 目标版本ID

        Returns:
            回退结果
        """
        try:
            chapter_versions = self.versions.get(chapter_id, [])

            if not chapter_versions:
                return {
                    "success": False,
                    "error": "章节不存在",
                    "message": f"章节 {chapter_id} 不存在"
                }

            # 查找目标版本
            target_version = None
            for version in chapter_versions:
                if version["version_id"] == target_version_id:
                    target_version = version
                    break

            if not target_version:
                return {
                    "success": False,
                    "error": "版本不存在",
                    "message": f"版本 {target_version_id} 不存在"
                }

            # 创建基于目标版本的新版本
            current_version = chapter_versions[-1]
            result = await self.create_version(
                chapter_id=chapter_id,
                content=target_version["content"],
                created_by="rollback",
                version_type="reverted",
                parent_version_id=current_version["version_id"]
            )

            if result["success"]:
                logger.info(f"版本回退成功: {chapter_id} -> {target_version_id}")
                return {
                    "success": True,
                    "rollback_to_version": target_version,
                    "new_version_id": result["version_id"],
                    "message": f"已回退到版本 {target_version['version_number']}，并创建新版本 {result['version_number']}"
                }
            else:
                return result

        except Exception as e:
            logger.error(f"版本回退异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "版本回退异常"
            }

    async def archive_version(
        self,
        chapter_id: str,
        version_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        归档版本

        Args:
            chapter_id: 章节ID
            version_id: 版本ID（不指定则归档最新版本）

        Returns:
            归档结果
        """
        try:
            chapter_versions = self.versions.get(chapter_id, [])

            if not chapter_versions:
                return {
                    "success": False,
                    "error": "章节不存在",
                    "message": f"章节 {chapter_id} 不存在"
                }

            # 确定要归档的版本
            if version_id:
                version_to_archive = None
                for version in chapter_versions:
                    if version["version_id"] == version_id:
                        version_to_archive = version
                        break

                if not version_to_archive:
                    return {
                        "success": False,
                        "error": "版本不存在",
                        "message": f"版本 {version_id} 不存在"
                    }
            else:
                version_to_archive = chapter_versions[-1]
                version_id = version_to_archive["version_id"]

            # 归档版本
            version_to_archive["status"] = "archived"
            version_to_archive["archived_at"] = datetime.now().isoformat()

            # 添加到归档列表
            if chapter_id not in self.archived_versions:
                self.archived_versions[chapter_id] = []

            # 检查是否已归档
            already_archived = any(
                v["version_id"] == version_id
                for v in self.archived_versions[chapter_id]
            )

            if not already_archived:
                self.archived_versions[chapter_id].append(version_to_archive)

            logger.info(f"版本归档成功: {version_id}")

            return {
                "success": True,
                "archived_version": version_to_archive,
                "version_id": version_id,
                "message": f"版本 {version_id} 归档成功"
            }

        except Exception as e:
            logger.error(f"版本归档异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "版本归档异常"
            }

    def _find_version_by_id(self, version_id: str) -> Optional[Dict[str, Any]]:
        """根据ID查找版本"""
        for chapter_id, versions in self.versions.items():
            for version in versions:
                if version["version_id"] == version_id:
                    return version
        return None

    def _calculate_diff(self, content1: str, content2: str) -> str:
        """计算两个内容的差异"""
        # 简单实现：基于行级别的差异
        lines1 = content1.split('\n')
        lines2 = content2.split('\n')

        diff_lines = []
        max_lines = max(len(lines1), len(lines2))

        for i in range(max_lines):
            if i < len(lines1) and i < len(lines2):
                if lines1[i] != lines2[i]:
                    diff_lines.append(f"- {lines1[i]}")
                    diff_lines.append(f"+ {lines2[i]}")
            elif i < len(lines1):
                diff_lines.append(f"- {lines1[i]}")
            elif i < len(lines2):
                diff_lines.append(f"+ {lines2[i]}")

        return '\n'.join(diff_lines) if diff_lines else "无差异"


# 全局版本管理工具实例
_version_manager: Optional[VersionManager] = None


def get_version_manager() -> VersionManager:
    """获取版本管理工具单例"""
    global _version_manager
    if _version_manager is None:
        _version_manager = VersionManager()
    return _version_manager
