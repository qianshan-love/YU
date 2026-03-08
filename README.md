# 县志智能编纂Agent系统

基于LangGraph和ReAct模式的县志智能编纂系统，实现全流程自动化编纂、上下文长记忆留存、对话样本结构化存储。

## 项目特性

- **Plan and Execute模式调度中枢**：全局规划、执行协调、监控调度、状态管理
- **ReAct模式功能Agent**：6个功能Agent，各司其职，灵活应变
- **Agent托管式版本控制**：用户零操作，Agent全自动管理版本
- **分章节审核**：逐章节质量管控，支持审核驳回修改
- **完整工作流程**：9个阶段从需求问询到归档保存的完整闭环

## 项目结构

```
county-chronicles-agent/
├── config/                    # 配置文件
│   └── settings.py           # 项目配置
├── data/                     # 数据存储
├── logs/                     # 日志文件
├── src/
│   ├── agents/              # Agent模块
│   │   ├── __init__.py
│   │   ├── base_agent.py    # Agent基类
│   │   ├── dispatcher.py    # 调度中枢
│   │   ├── task_planner_agent.py   # 任务规划Agent
│   │   ├── drafting_agent.py       # 撰稿生成Agent
│   │   ├── review_agent.py         # 审校校验Agent
│   │   ├── version_agent.py         # 版本控制Agent
│   │   └── member_agent.py         # 成员管理Agent
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── state.py        # 状态模型
│   │   └── agent.py        # Agent模型
│   ├── tools/               # 工具模块
│   │   ├── http_client.py  # HTTP客户端（LLM调用）
│   │   └── ...
│   └── utils/               # 工具函数
│       ├── __init__.py
│       ├── logger.py        # 日志工具
│       └── helpers.py       # 辅助函数
├── main.py                  # 主入口
├── requirements.txt         # 依赖包
├── .env.example            # 环境变量示例
└── README.md               # 项目说明
```

## 技术栈

- **Agent框架**: LangGraph
- **后端框架**: Python + FastAPI
- **大模型**: Qwen3.5-35B 本地部署（GGUF格式）
- **数据存储**: MySQL + MongoDB + Redis + Elasticsearch

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd county-chronicles-agent

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑.env文件，配置大模型地址等参数
# MODEL_BASE_URL=http://192.168.0.106:8080/v1
```

### 3. 启动服务

```bash
# 启动API服务
python main.py

# 或使用uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 使用示例

#### 开始编纂任务

```bash
curl -X POST "http://localhost:8000/api/v1/compilation/start" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user001",
    "initial_requirements": {
      "county": "示例县",
      "purpose": "续修",
      "time_range": "2020-2025",
      "type": "综合志"
    },
    "members": [
      {
        "member_id": "user001",
        "name": "张三",
        "role": "editor",
        "expertise": ["经济", "政治"]
      }
    ]
  }'
```

#### 查询任务状态

```bash
curl "http://localhost:8000/api/v1/compilation/{task_id}/status"
```

#### 获取任务结果

```bash
curl "http://localhost:8000/api/v1/compilation/{task_id}/result"
```

## 编纂流程

```
1. 需求问询 → 与用户交互，明确编纂背景、目的、范围
2. 目录生成 → 基于需求生成符合国标的县志目录结构
3. 任务分配 → 根据成员数量动态分配撰稿、审核任务
4. 章节起草 → 逐章节生成初稿，自动生成版本
5. 章节审核 → 系统校验 + 人工审核，支持驳回修改
6. 稿件修改 → 根据审核意见修改，生成新版本
7. 终稿审核 → 整合所有章节，进行终稿审核
8. 最终确认 → 用户确认终稿
9. 归档保存 → 正式归档，锁定版本
```

## API文档

启动服务后访问 `http://localhost:8000/docs` 查看完整API文档。

## 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| MODEL_BASE_URL | 大模型API地址 | http://192.168.0.106:8080/v1 |
| MODEL_NAME | 模型名称 | Qwen3.5-35B-A3B-UD-Q4_K_XL |
| MODEL_TEMPERATURE | 温度参数 | 0.7 |
| MODEL_MAX_TOKENS | 最大token数 | 4096 |
| API_HOST | API监听地址 | 0.0.0.0 |
| API_PORT | API监听端口 | 8000 |

## 大模型配置

本项目使用本地部署的Qwen3.5-35B GGUF模型，通过API接口调用。

调用示例：
```bash
curl http://192.168.0.106:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.5-35B-A3B-UD-Q4_K_XL",
    "messages": [
      {"role": "user", "content": "你好，请介绍一下自己"}
    ],
    "temperature": 0.7,
    "max_tokens": 1024
  }'
```

## 开发说明

### 调度中枢

调度中枢采用**Plan and Execute**模式，负责：
- 全局规划：分析用户需求，生成编纂计划
- 执行协调：按计划调度功能Agent，监控执行进度
- 监控调度：全程跟踪进度，处理异常
- 状态维护：统一管理全局状态

### 功能Agent

功能Agent采用**ReAct**模式，包括：
- TaskPlannerAgent：需求问询、目录生成、任务分配
- DraftingAgent：章节起草、稿件修改、终稿整合
- ReviewAgent：章节审核、系统校验、终稿审核
- VersionAgent：版本生成、查询、对比、回退、归档
- MemberAgent：成员管理、任务重分配

### 添加新Agent

1. 继承`BaseAgent`类
2. 实现`get_agent_type()`方法
3. 实现`get_system_prompt()`方法
4. 实现`execute()`方法
5. 在调度中枢中注册新Agent

## 日志

日志文件位于`logs/app.log`，支持自动轮转。

日志级别可通过`.env`文件配置：
```
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 贡献指南

欢迎提交Issue和Pull Request。

## 许可证

MIT License
