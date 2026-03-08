# seasea 搜索引擎快速开始指南

## ⚡ 5分钟快速开始

### 步骤1：安装依赖（1分钟）

```bash
cd /e/county-chronicles-agent
pip install seesea
```

### 步骤2：配置环境（1分钟）

编辑 `.env` 文件：

```bash
# 启用 seasea 搜索
USE_SEASEA=true

# 默认搜索引擎
SEASEA_DEFAULT_ENGINE=baidu

# 搜索区域
SEASEA_REGION=china
```

### 步骤3：运行测试（3分钟）

```bash
# 测试 seasea 集成
python test_seasea_search.py
```

---

## 🎯 验证成功标志

看到以下输出说明集成成功：

```
✓ seasea 库已安装
✓ 搜索器创建成功
✓ 搜索成功，找到 X 条结果
✓ seasea 搜索引擎可用
```

---

## 💻 使用示例

### 示例1：基础搜索

```python
from src.tools.web_search import get_web_search_tool

# 获取搜索工具
web_tool = get_web_search_tool()

# 搜索（自动使用 seasea）
result = await web_tool.search("县志编纂")

# 查看结果
print(result['data']['results'])
```

### 示例2：指定搜索引擎

```python
# 使用百度搜索
result = await web_tool.search("经济发展", engine="baidu")

# 使用 Bing 搜索
result = await web_tool.search("地方志", engine="bing")

# 使用 360 搜索
result = await web_tool.search("县志规范", engine="360")
```

### 示例3：在 Agent 中使用

```python
from src.agents.knowledge_agent import KnowledgeAgent
from src.models.agent import AgentTask

# 创建 KnowledgeAgent
knowledge = KnowledgeAgent({})

# 创建任务
task = AgentTask(
    task_id="task_001",
    agent_type="knowledge",
    action="retrieve_knowledge",
    params={
        "query": "县志编纂规范",
        "source": "knowledge_base"  # 自动触发 seasea 网络搜索
        "limit": 5
    },
    context={}
)

# 执行
result = await knowledge.execute(task)

# 结果：知识库检索 + seasea 网络搜索补充
```

---

## 📊 支持的搜索引擎

| 引擎 | 命令 | 说明 |
|------|------|------|
| 百度 | `baidu` | 国内最常用 |
| Bing | `bing` | 搜索质量高 |
| 360 | `360` | 结果全面 |
| 搜狗 | `so` | 专业性好 |
| 搜狗 | `sogou` | 专业性好 |

---

## 🔧 环境变量说明

| 变量 | 值 | 说明 |
|------|-----|------|
| `USE_SEASEA` | `true`/`false` | 是否启用 seasea |
| `SEASEA_DEFAULT_ENGINE` | `baidu`/`bing`/`360`/`so`/`sogou` | 默认引擎 |
| `SEASEA_REGION` | `china`/`international` | 搜索区域 |

---

## 🎉 快速验证

### 测试1：直接使用 seasea

```python
from seesea import Searcher

searcher = Searcher(region="china")
results = searcher.search("县志编纂", engine="baidu")

for result in results[:3]:
    print(f"标题: {result['title']}")
    print(f"URL: {result['url']}")
```

### 测试2：通过 WebSearchTool 使用

```python
from src.tools.web_search import get_web_search_tool

web_tool = get_web_search_tool()
result = await web_tool.search("县志编纂")

print(f"数据源: {result['data']['source']}")
print(f"结果数: {result['data']['total']}")
```

---

## 📞 常见问题

### Q: 如何切换搜索引擎？

**A**: 在调用时指定 `engine` 参数：

```python
result = await web_tool.search("关键词", engine="bing")
```

### Q: 知识库无结果怎么办？

**A**: 系统会自动触发 seasea 网络搜索补充，无需手动操作。

### Q: 搜索结果不准确？

**A**: 可以：
1. 切换搜索引擎（如从 baidu 切换到 bing）
2. 调整搜索关键词
3. 添加时间限定词

### Q: 如何确认 seasea 已启用？

**A**: 查看启动日志：

```
✓ seasea搜索引擎可用
```

---

## 📚 更多文档

- `SEASEA_SEARCH_GUIDE.md` - 详细配置指南
- `SEASEA_INTEGRATION_SUMMARY.md` - 集成总结
- `test_seasea_search.py` - 测试脚本

---

## ✅ 完成检查

- [x] 安装 seesea 依赖
- [x] 配置环境变量
- [x] 运行测试脚本
- [x] 验证搜索功能
- [x] 查看搜索结果

**全部勾选即表示配置成功！** 🎉
