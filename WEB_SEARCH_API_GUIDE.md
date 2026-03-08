# 真实网络搜索API配置指南

## 概述

本系统支持接入真实的网络搜索API，目前支持：
- **Bing Web Search API**（推荐，免费额度较大）
- **Google Custom Search API**

## 方案一：Bing Web Search API（推荐）

### 1. 获取API Key

1. 访问 [Azure Bing Web Search](https://azure.microsoft.com/en-us/services/cognitive-services/bing-web-search-api/)
2. 点击"免费"开始免费试用
3. 创建Azure账号并登录
4. 创建"Bing Web Search"资源
5. 在资源页面找到"Keys and Endpoint"
6. 复制API Key

### 2. 配置环境变量

编辑项目根目录的 `.env` 文件：

```bash
BING_API_KEY=your_actual_bing_api_key_here
```

### 3. 使用

无需修改代码，系统会自动检测并使用Bing API：

```python
from src.tools.web_search import get_web_search_tool

web_tool = get_web_search_tool()

# 自动使用Bing API（如果已配置）
result = await web_tool.search("地方志编纂", source="auto")
```

### 4. 免费额度

- **免费层级**：每月1,000次查询
- **S1层级**：$3/月，最高3,000次查询/月
- **S2层级**：$20/月，最高20,000次查询/月

---

## 方案二：Google Custom Search API

### 1. 创建自定义搜索引擎

1. 访问 [Google Programmable Search](https://programmablesearchengine.google.com/)
2. 点击"添加"创建搜索引擎
3. 配置搜索引擎：
   - "要搜索的网站或域名"：输入 `*`（搜索整个互联网）或特定域名
   - "搜索引擎的名称"：输入名称，如"County Chronicles"
   - 点击"创建"
4. 在控制面板页面，记录"搜索引擎ID"

### 2. 启用API

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 在API库中搜索"Custom Search API"
4. 点击"启用"
5. 在凭据页面创建API Key

### 3. 配置环境变量

编辑 `.env` 文件：

```bash
GOOGLE_API_KEY=your_actual_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

### 4. 使用

```python
from src.tools.web_search import get_web_search_tool

web_tool = get_web_search_tool()

# 使用Google API
result = await web_tool.search("地方志编纂", source="google")
```

### 5. 免费额度

- **免费层级**：每天100次查询
- **付费层级**：$5/10,000次查询

---

## 数据源选择

系统支持以下搜索源：

| 数据源 | 配置 | 说明 |
|--------|------|------|
| `auto` | 自动选择 | 优先使用真实API，无API时使用模拟数据 |
| `mock` | 无需配置 | 使用本地模拟数据，适合开发测试 |
| `bing` | 需BING_API_KEY | 使用Bing Web Search API |
| `google` | 需GOOGLE_API_KEY和GOOGLE_SEARCH_ENGINE_ID | 使用Google Custom Search API |
| `custom` | 需自定义实现 | 自定义搜索API |

### 使用示例

```python
# 自动选择（推荐）
result = await web_tool.search("关键词", source="auto")

# 强制使用Bing
result = await web_tool.search("关键词", source="bing")

# 强制使用Google
result = await web_tool.search("关键词", source="google")

# 使用模拟数据（无需API Key）
result = await web_tool.search("关键词", source="mock")
```

---

## 降级机制

系统内置智能降级机制：

1. **API失败时自动降级**
   - 如果真实API调用失败，自动降级到模拟数据
   - 保证系统稳定性

2. **API未配置时使用模拟数据**
   - 检测到未配置API Key时，自动使用模拟数据
   - 不影响系统运行

---

## 测试API配置

### 测试Bing API

创建测试脚本 `test_bing_api.py`：

```python
import asyncio
import os
from src.tools.web_search import get_web_search_tool

async def test_bing():
    # 配置API Key
    os.environ["BING_API_KEY"] = "your_api_key"

    web_tool = get_web_search_tool()

    # 测试搜索
    result = await web_tool.search("地方志编纂", source="bing")
    print(f"搜索结果: {result}")

asyncio.run(test_bing())
```

### 测试Google API

创建测试脚本 `test_google_api.py`：

```python
import asyncio
import os
from src.tools.web_search import get_web_search_tool

async def test_google():
    # 配置API Key
    os.environ["GOOGLE_API_KEY"] = "your_api_key"
    os.environ["GOOGLE_SEARCH_ENGINE_ID"] = "your_search_engine_id"

    web_tool = get_web_search_tool()

    # 测试搜索
    result = await web_tool.search("地方志编纂", source="google")
    print(f"搜索结果: {result}")

asyncio.run(test_google())
```

---

## 常见问题

### Q1: 为什么搜索返回空结果？

**A**: 检查以下几点：
1. API Key是否正确配置
2. API Key是否有效（检查是否过期）
3. 是否超出免费额度
4. 网络连接是否正常

### Q2: 搜索结果不准确怎么办？

**A**:
1. 尝试使用更精确的搜索关键词
2. 调整搜索参数（如语言、地区）
3. 使用多个数据源并对比结果

### Q3: 如何提高搜索性能？

**A**:
1. 使用缓存机制（Redis）
2. 批量搜索时使用`batch_search`方法
3. 合理设置`timeout`参数

### Q4: 是否支持其他搜索API？

**A**: 支持自定义搜索API，请参考`_custom_search`方法进行实现。

---

## 安全建议

1. **不要将API Key提交到版本控制**
   - 使用`.env`文件存储
   - 将`.env`添加到`.gitignore`

2. **定期轮换API Key**
   - 定期更新API Key
   - 使用不同环境的API Key（开发/测试/生产）

3. **监控API使用量**
   - 定期检查API使用情况
   - 避免超出免费额度

---

## 总结

**推荐配置**：
- 开发/测试环境：使用 `mock` 模式
- 生产环境：使用 `bing` 或 `google` API

**优势**：
- 自动降级机制，保证稳定性
- 支持多种搜索源，灵活选择
- 配置简单，开箱即用
