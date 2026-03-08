# seesea 搜索引擎集成指南

## 概述

本系统已集成 **seesea** 轻量级 Python 搜索库，支持国内主流搜索引擎：
- 百度（Baidu）
- Bing 国内版
- 360 搜索
- 搜狗（Sogou）
- 有道（Youdao）

**优势**：
- ✅ 无需 API Key
- ✅ 国内搜索速度快
- ✅ 支持多个搜索引擎
- ✅ 简单易用

---

## 安装 seesea

```bash
pip install seesea
```

---

## 配置方式

### 方法1：环境变量配置（推荐）

编辑项目根目录的 `.env` 文件：

```bash
# 启用 seesea（推荐）
USE_SEASEA=true

# 默认搜索引擎
SEASEA_DEFAULT_ENGINE=baidu

# 搜索区域
SEASEA_REGION=china
```

### 方法2：Python 代码配置

```python
from seesea import Searcher

# 创建搜索器实例
searcher = Searcher(region="china")  # 强制国内引擎

# 搜索
results = searcher.search("AI Agent", engine="baidu")
```

---

## 支持的搜索引擎

| 引擎名称 | 说明 | 是否需要API Key |
|---------|------|----------------|
| `baidu` | 百度搜索 | ❌ 不需要 |
| `bing` | Bing国内版 | ❌ 不需要 |
| `360` | 360搜索 | ❌ 不需要 |
| `so` | 搜狗搜索 | ❌ 不需要 |
| `sogou` | 搜狗搜索 | ❌ 不需要 |
| `youdao` | 有道搜索 | ❌ 不需要 |

---

## 使用示例

### 1. 基础搜索

```python
from seesea import Searcher

# 创建搜索器
searcher = Searcher(region="china")

# 百度搜索
results = searcher.search("县志编纂", engine="baidu")

# Bing 搜索
results = searcher.search("地方志", engine="bing")

# 360 搜索
results = searcher.search("地方志编纂规范", engine="360")
```

### 2. 在本系统中使用

```python
from src.tools.web_search import get_web_search_tool

# 获取搜索工具实例
web_tool = get_web_search_tool()

# 使用 seesea 搜索（自动）
result = await web_tool.search("地方志编纂")

# 指定使用 seesea
result = await web_tool.search("县志规范", source="seesea")

# 指定使用特定引擎
result = await web_tool.search("经济发展", engine="bing")
```

### 3. 批量搜索

```python
from seesea import Searcher

searcher = Searcher(region="china")

# 批量搜索
queries = ["县志编纂", "经济发展", "人口统计"]

for query in queries:
    results = searcher.search(query, engine="baidu")
    for result in results:
        print(f"标题: {result['title']}")
        print(f"URL: {result['url']}")
        print(f"描述: {result['description']}")
```

---

## 配置选项详解

### USE_SEASEA

- `true`: 启用 seesea 搜索（推荐）
- `false`: 禁用 seesea，使用其他搜索方式

### SEASEA_DEFAULT_ENGINE

设置默认搜索引擎：

| 值 | 说明 |
|---|------|
| `baidu` | 百度搜索（默认，推荐） |
| `bing` | Bing国内版 |
| `360` | 360搜索 |
| `so` | 搜狗搜索 |
| `sogou` | 搜狗搜索 |

### SEASEA_REGION

设置搜索区域：

| 值 | 说明 |
|---|------|
| `china` | 国内搜索（默认，推荐） |
| `international` | 国际搜索 |

---

## 搜索引擎选择建议

### 国内使用场景

| 场景 | 推荐引擎 | 原因 |
|------|---------|------|
| 日常搜索 | `baidu` | 国内用户最常用 |
| 学术搜索 | `bing` | 搜索质量高 |
| 综合搜索 | `360` | 结果全面 |

### 特定内容搜索

| 内容类型 | 推荐引擎 | 原因 |
|---------|---------|------|
| 新闻资讯 | `baidu` | 实时性好 |
| 学术资源 | `bing` | 权威性强 |
| 资料文档 | `360` | 涵盖面广 |
| 专业内容 | `so` | 专业性好 |

---

## 系统集成说明

### 自动优先级

系统会按以下优先级选择搜索方式：

1. **seesea**（如果已安装并启用）
2. **Bing API**（如果已配置）
3. **Google API**（如果已配置）
4. **模拟数据**（后备方案）

### 降级机制

```
seesea 失败 → 尝试 Bing API → 尝试 Google API → 降级到模拟数据
```

### 使用方式

```python
# 自动选择（推荐）
result = await web_tool.search("关键词", source="auto")

# 强制使用 seesea
result = await web_tool.search("关键词", source="seesea")

# 指定搜索引擎
result = await web_tool.search("关键词", engine="bing")

# 使用 Bing API
result = await web_tool.search("关键词", source="bing")

# 使用 Google API
result = await web_tool.search("关键词", source="google")

# 使用模拟数据
result = await web_tool.search("关键词", source="mock")
```

---

## 性能对比

| 搜索方式 | 速度 | 准确性 | 成本 |
|---------|------|--------|------|
| **seesea (百度)** | ⚡⚡⚡ 快 | ⭐⭐⭐⭐ 好 | 免费 |
| **seesea (Bing)** | ⚡⚡ 快 | ⭐⭐⭐⭐⭐ 优秀 | 免费 |
| **Bing API** | ⚡⚡ 快 | ⭐⭐⭐⭐⭐ 优秀 | 收费 |
| **Google API** | ⚡ 快 | ⭐⭐⭐⭐⭐ 优秀 | 收费 |
| **模拟数据** | ⚡⚡⚡⚡ 最快 | ⭐⭐ 一般 | 免费 |

---

## 常见问题

### Q1: seesea 搜索没有结果怎么办？

**A**: 可以尝试：
1. 切换搜索引擎（如从 baidu 切换到 bing）
2. 调整搜索关键词
3. 检查网络连接

### Q2: 如何提高搜索准确性？

**A**:
1. 使用更精确的关键词
2. 添加时间限定词（如"2024年"）
3. 使用多关键词搜索（如"县志 编纂"）

### Q3: seesea 和 Bing API 哪个更好？

**A**:
- **国内使用**: 推荐 seesea（免费、快速）
- **国际使用**: 推荐 Bing API（结果质量高）
- **成本考虑**: seesea 完全免费

### Q4: 如何调试搜索功能？

**A**:
```python
# 设置日志级别为 DEBUG
import logging
logging.basicConfig(level=logging.DEBUG)

# 执行搜索
result = await web_tool.search("关键词")

# 查看详细日志
```

---

## 高级用法

### 1. 自定义搜索参数

```python
from seesea import Searcher

searcher = Searcher(region="china")

# 百度搜索（带参数）
results = searcher.search(
    "县志编纂",
    engine="baidu"
)

# 可以在调用时指定更多参数（需要查看 seesea 文档）
```

### 2. 搜索结果过滤

```python
# 搜索后过滤结果
results = searcher.search("地方志", engine="baidu")

# 过滤特定域名
filtered_results = [
    r for r in results
    if "gov.cn" in r.get("url", "")
]

# 过滤特定标题
filtered_results = [
    r for r in results
    if "县志" in r.get("title", "")
]
```

### 3. 搜索结果缓存

```python
# 使用 Redis 缓存搜索结果（提高性能）
import redis

redis_client = redis.Redis()

# 检查缓存
cached_key = f"search:{query}:{engine}"
cached_result = redis_client.get(cached_key)

if cached_result:
    results = json.loads(cached_result)
else:
    # 执行搜索
    results = searcher.search(query, engine=engine)

    # 缓存结果（1小时过期）
    redis_client.setex(cached_key, 3600, json.dumps(results))
```

---

## 总结

**推荐配置**：

```bash
# .env 文件
USE_SEASEA=true
SEASEA_DEFAULT_ENGINE=baidu
SEASEA_REGION=china
```

**使用方式**：

```python
from src.tools.web_search import get_web_search_tool

web_tool = get_web_search_tool()

# 自动选择最佳搜索方式
result = await web_tool.search("县志编纂", source="auto")
```

**优势**：
- ✅ 无需 API Key
- ✅ 国内搜索速度快
- ✅ 多搜索引擎支持
- ✅ 智能降级机制
- ✅ 开箱即用

---

## 参考资料

- seesea GitHub: https://github.com/seasea/seasea
- seesea 文档: https://github.com/seesea/seasea/blob/main/README.md
- Python 文档: https://docs.python.org/3/
