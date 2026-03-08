# 县志智能编纂Agent系统

## 📋 项目概述

基于LangGraph和ReAct模式的县志智能编纂系统，实现全流程自动化编纂、上下文长记忆留存、对话样本结构化存储。

## 🎯 核心特性

- **Plan and Execute模式调度中枢**：全局规划、执行协调、监控调度、状态管理
- **ReAct模式功能Agent**：6个功能Agent，各司其职，灵活应变
- **Agent托管式版本控制**：用户零操作，Agent全自动管理版本
- **分章节审核**：逐章节质量管控，支持审核驳回修改
- **完整工作流程**：9个阶段从需求问询到归档保存的完整闭环
- **大模型集成**：Qwen3.5-35B-A3B-UD-Q4_K_XL，支持多轮对话
- **多数据源支持**：seesea（国内）→ Bing API → Google API → mock数据
- **调试界面**：Agent状态监控、大模型测试、系统日志查看

## 🚀 快速开始

### 1. 启动调试界面
```bash
python debug_interface_optimized.py
```

**访问地址：**
- 调试界面：http://localhost:8001
- API文档：http://localhost:8001/docs
- 项目状态：查看 `PROJECT_STATUS.md`

### 2. 运行主程序
```bash
python main.py
```

### 3. 查看详细状态
项目完成度和待完成工作请查看 `PROJECT_STATUS.md`

## 🏗️ 项目结构

```
county-chronicles-agent/
├── config/                    # 配置文件
│   └── settings.py           # 项目配置
├── data/                     # 数据存储（待实现）
│   ├── knowledge_base/          # 知识库数据
│   ├── versions/              # 版本数据
│   └── execution_logs/        # 执行日志
├── src/
│   ├── agents/              # Agent模块
│   │   ├── __init__.py
│   │   ├── base_agent.py    # Agent基类 ✅
│   │   ├── dispatcher.py    # 调度中枢 ✅
│   │   ├── task_planner_agent.py   # 任务规划Agent ✅
│   │   ├── drafting_agent.py       # 撰稿生成Agent ✅
│   │   ├── review_agent.py         # 审校校验Agent ✅
│   │   ├── version_agent.py         # 版本控制Agent ✅
│   │   └── member_agent.py         # 成员管理Agent ✅
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── state.py        # 状态模型 ✅
│   │   └── agent.py        # Agent模型 ✅
│   └── tools/               # 工具模块
│       ├── content_generation.py  # 内容生成 ✅
│       ├── http_client.py  # HTTP客户端 ✅
│       ├── llm_service.py      # LLM服务 ✅
│       ├── retrieval.py        # 知识检索 ✅
│       ├── specification.py    # 规范查询 ✅
│       ├── system_validation.py # 系统校验 ✅
│       ├── user_interaction.py # 用户交互 ✅
│       ├── version_manager.py  # 版本管理 ✅
│       └── web_search.py      # 网络搜索 ✅
│   └── utils/               # 工具函数
│       ├── __init__.py
│       ├── logger.py        # 日志工具 ✅
│       └── helpers.py       # 辅助函数 ✅
├── debug_interface_optimized.py  # 调试界面（优化版） ✅
├── main.py                  # 主入口 ✅
├── requirements.txt         # 依赖包 ✅
├── .env.example            # 环境变量示例 ✅
├── DESIGN.md               # 设计文档 ✅
├── IMPLEMENTATION_SUMMARY.md  # 实现总结 ✅
├── DEBUG_INTERFACE_GUIDE.md  # 调试界面指南 ✅
└── PROJECT_STATUS.md        # 项目状态文档 ✅
```

## 🤖 Agent架构

### 调度中枢 Agent (Dispatcher) ✅
- **功能**：全局规划、任务协调、监控调度、状态管理
- **设计模式**：Plan and Execute
- **实现进度**：90%
- **主要功能**：任务分配、Agent调度、状态机管理

### 功能执行Agent (6个) ✅

#### 1. 任务规划 Agent (TaskPlannerAgent) ✅
- **功能**：需求问询、目录生成、任务分配
- **设计模式**：ReAct
- **实现进度**：65%
- **依赖工具**：内容生成、用户交互

#### 2. 知识规范 Agent (KnowledgeAgent) ✅
- **功能**：规范查询、知识检索、网络搜索、规范校验
- **设计模式**：ReAct
- **实现进度**：75%
- **依赖工具**：规范查询、知识检索、网络搜索

#### 3. 撰稿生成 Agent (DraftingAgent) ✅
- **功能**：章节起草、内容生成、版本管理
- **设计模式**：ReAct
- **实现进度**：60%
- **依赖工具**：内容生成、版本管理、系统校验

#### 4. 审校校验 Agent (ReviewAgent) ✅
- **功能**：系统校验、人工审核、版本对比、事实一致性检查
- **设计模式**：ReAct
- **实现进度**：50%
- **依赖工具**：系统校验、版本对比

#### 5. 版本控制 Agent (VersionAgent) ✅
- **功能**：版本生成、查询、对比、回退、归档
- **设计模式**：ReAct
- **实现进度**：55%
- **依赖工具**：版本管理

#### 6. 成员管理 Agent (MemberAgent) ✅
- **功能**：成员管理、任务重分配、通知发送
- **设计模式**：ReAct
- **实现进度**：50%
- **依赖工具**：用户交互

## 🛠️ 工具层

### 已实现工具（8个）

#### 1. 大模型服务 ✅
- **文件**：`src/tools/llm_service.py`
- **功能**：对话、文本生成、流式输出、工具调用支持
- **模型**：Qwen3.5-35B-A3B-UD-Q4_K_XL
- **API地址**：http://140.143.163.123:59655/v1/chat/completions

#### 2. 内容生成工具 ✅
- **文件**：`src/tools/content_generation.py`
- **功能**：章节生成、目录生成、小节生成、内容改进
- **集成**：使用LLM服务

#### 3. 版本管理工具 ✅
- **文件**：`src/tools/version_manager.py`
- **功能**：版本CRUD、版本对比、版本回退、版本归档
- **实现**：内存存储（实际应使用数据库）

#### 4. 用户交互工具 ✅
- **文件**：`src/tools/user_interaction.py`
- **功能**：用户问答、需求问询、通知发送、问题历史管理

#### 5. 系统校验工具 ✅
- **文件**：`src/tools/system_validation.py`
- **功能**：体例校验、格式校验、事实校验
- **规则**：预设校验规则（体例、格式、事实）

#### 6. 网络搜索工具 ✅
- **文件**：`src/tools/web_search.py`
- **功能**：多数据源支持（seesea、bing、google、mock）
- **当前状态**：seesea因Windows权限问题使用mock数据
- **降级机制**：seesea → bing → google → mock

#### 7. 规范查询工具 ✅
- **文件**：`src/tools/specification.py`
- **功能**：县志规范查询和内容校验

#### 8. 知识检索工具 ✅
- **文件**：`src/tools/retrieval.py`
- **功能**：知识库检索、网络搜索补充

## 🔧 调试界面

### 优化版调试界面 ✅
- **文件**：`debug_interface_optimized.py`
- **端口**：8001（与原版8000不同，可同时运行）
- **主要功能**：
  - ✅ Agent工作状态实时监控（6个Agent）
  - ✅ 大模型对话测试
  - ✅ 系统日志实时查看（类型着色）
  - ✅ Agent功能快速测试
  - ✅ 自动状态刷新（10秒间隔）

### 访问方式
```bash
# 启动调试界面
python debug_interface_optimized.py

# 访问地址
http://localhost:8001
```

## 📊 技术栈

### 核心技术
- **Agent框架**：LangGraph (调度中枢) + ReAct (功能Agent)
- **后端框架**：FastAPI
- **异步处理**：asyncio
- **大模型**：Qwen3.5-35B-A3B-UD-Q4_K_XL
- **日志系统**：自定义日志系统
- **配置管理**：环境变量 + 配置文件

### 主要依赖
- **HTTP客户端**：httpx
- **异步框架**：asyncio
- **Web框架**：FastAPI
- **API服务**：Uvicorn
- **JSON处理**：Python json

## 🎯 使用指南

### 1. 调试和监控
1. 启动调试界面：`python debug_interface_optimized.py`
2. 监控Agent状态：查看6个Agent的实时状态
3. 测试大模型：在调试界面测试Qwen3.5-35B调用
4. 查看系统日志：实时了解系统运行情况

### 2. Agent功能测试
1. 选择要测试的Agent
2. 点击"测试"按钮执行功能
3. 查看执行结果和日志
4. 根据结果调试问题

### 3. 项目状态查看
详细的完成度和待完成工作请查看 `PROJECT_STATUS.md`

## 🎉 当前状态

### 已完成模块
- ✅ Agent框架和调度中枢（90%完成）
- ✅ 6个功能Agent（基础架构完成）
- ✅ 大模型集成（Qwen3.5-35B）
- ✅ 工具层实现（7个核心工具）
- ✅ 调试界面（优化版，支持监控）

### 待完成模块
- ⏳ 数据库实现（MySQL + MongoDB + Redis）
- ⏳ Agent功能完善（工具集成）
- ⏳ 规则引擎扩展
- ⏳ 完整流程测试
- ⏳ 性能优化

### 总体完成度
**约60%** - 核心架构和工具层完成，可以进行Agent集成和数据库开发

## 📝 详细文档

- **PROJECT_STATUS.md** - 项目状态总览，包含所有模块的完成度
- **DESIGN.md** - 系统架构设计文档
- **IMPLEMENTATION_SUMMARY.md** - 功能实现总结
- **DEBUG_INTERFACE_GUIDE.md** - 调试界面使用指南

## 🔗️ Git配置

**仓库地址**：`git@github.com:qianshan-love/YU.git`
**当前分支**：`main`

**分支使用建议**：
- `main` - 稳定开发分支
- 新功能开发 - 创建新特性分支
- 问题修复 - 创建问题修复分支

---

**🎉 项目架构完整，核心功能已实现，可以开始Agent集成和数据库开发！**

**主要优势：**
- 模块化设计，易于扩展
- 完整的ReAct和LangGraph架构
- 实时Agent状态监控
- 多数据源支持，提高可用性
- 大模型集成，支持复杂的县志编纂任务

### 3. 查看项目状态
详细的完成度和待完成工作请查看 `PROJECT_STATUS.md`
