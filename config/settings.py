"""
项目配置文件
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """项目配置"""

    # ========== 项目基础配置 ==========
    PROJECT_NAME: str = "County Chronicles Agent"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ========== 大模型配置 ==========
    MODEL_BASE_URL: str = "http://192.168.0.106:8080/v1"
    MODEL_NAME: str = "Qwen3.5-35B-A3B-UD-Q4_K_XL"
    MODEL_TEMPERATURE: float = 0.7
    MODEL_MAX_TOKENS: int = 4096
    MODEL_TIMEOUT: int = 300  # 5分钟超时

    # ========== API配置 ==========
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"

    # ========== 数据库配置 ==========
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017/"
    MONGODB_DB_NAME: str = "county_chronicles"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # Elasticsearch
    ES_HOST: str = "localhost"
    ES_PORT: int = 9200
    ES_INDEX_PREFIX: str = "county_chronicles"

    # ========== 任务配置 ==========
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5  # 秒
    MAX_ITERATIONS: int = 10  # ReAct最大迭代次数

    # ========== 超时配置 ==========
    AGENT_TIMEOUT: int = 600  # 10分钟
    TASK_TIMEOUT: int = 3600  # 1小时
    REVIEW_TIMEOUT: int = 86400  # 24小时

    # ========== 日志配置 ==========
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_MAX_BYTES: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


# 全局配置实例
settings = get_settings()
