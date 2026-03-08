"""
临时调试界面
用于测试和调试Agent系统，实际项目中不需要
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agents.dispatcher import get_dispatcher
from src.models.agent import AgentTask
from src.tools.llm_service import get_llm_service

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="县志Agent调试界面", version="0.1.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 数据模型 ============

class ChatMessage(BaseModel):
    role: str
    content: str


class AgentRequest(BaseModel):
    agent_type: str
    action: str
    params: Dict[str, Any] = {}
    context: Dict[str, Any] = {}


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: Optional[float] = None


# ============ 页面模板 ============

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>县志Agent调试界面</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
        }
        .header p {
            margin: 5px 0 0;
            opacity: 0.9;
            font-size: 14px;
        }
        .main-content {
            display: grid;
            grid-template-columns: 350px 1fr 350px;
            gap: 20px;
            padding: 20px;
            height: calc(100vh - 140px);
        }
        .panel {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            overflow-y: auto;
            background: #f9f9f9;
        }
        .panel h2 {
            color: #667eea;
            font-size: 18px;
            margin: 0 0 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        .agent-card {
            background: white;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 10px;
            border-left: 3px solid #667eea;
            transition: all 0.3s;
        }
        .agent-card:hover {
            transform: translateX(5px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .agent-card h3 {
            margin: 0 0 5px;
            font-size: 14px;
            color: #333;
        }
        .agent-card p {
            margin: 0;
            font-size: 12px;
            color: #666;
        }
        textarea {
            width: 100%;
            min-height: 100px;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 10px;
            font-family: inherit;
            resize: vertical;
            margin-bottom: 10px;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
            margin-right: 5px;
            margin-bottom: 5px;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102,126,234,0.4);
        }
        button:active {
            transform: translateY(0);
        }
        .chat-container {
            height: calc(100% - 150px);
            overflow-y: auto;
            background: white;
            border-radius: 6px;
            padding: 10px;
            margin-bottom: 10px;
        }
        .chat-message {
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 6px;
            max-width: 80%%;
        }
        .chat-message.user {
            background: #667eea;
            color: white;
            margin-left: auto;
        }
        .chat-message.assistant {
            background: #f0f0f0;
            color: #333;
            margin-right: auto;
        }
        .log-entry {
            font-family: 'Courier New', monospace;
            font-size: 11px;
            padding: 5px;
            margin-bottom: 5px;
            border-left: 2px solid #ddd;
            background: white;
        }
        .log-entry.error {
            border-left-color: #e74c3c;
            color: #c0392b;
        }
        .log-entry.success {
            border-left-color: #27ae60;
            color: #27ae60;
        }
        .status-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
            margin-left: 5px;
        }
        .status-success {
            background: #d4edda;
            color: #155724;
        }
        .status-pending {
            background: #fff3cd;
            color: #856404;
        }
        .status-error {
            background: #f8d7da;
            color: #721c24;
        }
        input, select {
            width: 100%%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 10px;
            font-size: 14px;
        }
        .result-box {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 15px;
            margin-top: 10px;
            font-size: 13px;
            line-height: 1.6;
        }
        .tabs {
            display: flex;
            margin-bottom: 15px;
            border-bottom: 2px solid #e0e0e0;
        }
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
            transition: all 0.3s;
        }
        .tab:hover {
            background: #f0f0f0;
        }
        .tab.active {
            border-bottom-color: #667eea;
            color: #667eea;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 县志智能编纂Agent调试界面</h1>
            <p>临时开发用于调试，实际项目中不需要</p>
        </div>

        <div class="main-content">
            <!-- 左侧面板：Agent控制 -->
            <div class="panel">
                <h2>🤖 Agent控制</h2>

                <div class="tabs">
                    <div class="tab active" onclick="switchTab('control')">控制</div>
                    <div class="tab" onclick="switchTab('llm')">大模型</div>
                    <div class="tab" onclick="switchTab('status')">状态</div>
                </div>

                <!-- 控制标签页 -->
                <div id="tab-control" style="display: block;">
                    <div style="margin-bottom: 15px;">
                        <label style="font-weight: bold;">Agent类型：</label>
                        <select id="agentType" onchange="updateAgentInfo()">
                            <option value="task_planner">任务规划 (TaskPlanner)</option>
                            <option value="knowledge">知识规范 (Knowledge)</option>
                            <option value="drafting">撰稿生成 (Drafting)</option>
                            <option value="review">审校校验 (Review)</option>
                            <option value="version">版本控制 (Version)</option>
                            <option value="member">成员管理 (Member)</option>
                        </select>
                    </div>

                    <div style="margin-bottom: 15px;">
                        <label style="font-weight: bold;">操作类型：</label>
                        <select id="actionType">
                            <option value="generate_text">生成文本</option>
                            <option value="query_knowledge">查询知识</option>
                            <option value="validate_content">校验内容</option>
                            <option value="search_web">网络搜索</option>
                        </select>
                    </div>

                    <div style="margin-bottom: 15px;">
                        <label style="font-weight: bold;">参数（JSON）：</label>
                        <textarea id="paramsInput" placeholder='{"prompt": "示例提示词"}'></textarea>
                    </div>

                    <button onclick="executeAgent()">执行Agent任务</button>
                    <button onclick="quickTest()">快速测试</button>
                </div>

                <!-- 大模型标签页 -->
                <div id="tab-llm" style="display: none;">
                    <div style="margin-bottom: 15px;">
                        <label style="font-weight: bold;">系统提示词：</label>
                        <textarea id="systemPrompt" rows="3" placeholder="系统提示词..."></textarea>
                    </div>

                    <div style="margin-bottom: 15px;">
                        <label style="font-weight: bold;">用户消息：</label>
                        <textarea id="userMessage" rows="3" placeholder="你的问题..."></textarea>
                    </div>

                    <div style="margin-bottom: 15px;">
                        <label style="font-weight: bold;">温度参数：0.7</label>
                        <input type="range" id="temperature" min="0" max="1" step="0.1" value="0.7">
                    </div>

                    <button onclick="chatWithLLM()">对话大模型</button>
                </div>

                <!-- 状态标签页 -->
                <div id="tab-status" style="display: none;">
                    <div id="agentList">
                        <!-- Agent列表动态生成 -->
                    </div>
                </div>
            </div>

            <!-- 中间面板：聊天区域 -->
            <div class="panel">
                <h2>💬 对话区域</h2>

                <div class="chat-container" id="chatContainer">
                    <div class="chat-message assistant">
                        欢迎使用县志Agent调试界面！
                        <br><br>
                        功能包括：
                        <ul style="margin: 10px 0 10px 20px;">
                            <li>Agent控制：执行各Agent的任务</li>
                            <li>大模型对话：直接测试LLM调用</li>
                            <li>日志查看：实时查看系统日志</li>
                            <li>快速测试：一键测试基本功能</li>
                        </ul>
                    </div>
                </div>

                <div style="margin-top: 10px;">
                    <textarea id="chatInput" rows="2" placeholder="输入消息..." onkeypress="if(event.key==='Enter' && !event.shiftKey){event.preventDefault();sendMessage();}"></textarea>
                    <button onclick="sendMessage()" style="margin-top: 5px;">发送消息</button>
                    <button onclick="clearChat()" style="background: #6c757d;">清空对话</button>
                </div>
            </div>

            <!-- 右侧面板：结果和日志 -->
            <div class="panel">
                <h2>📊 执行结果</h2>

                <div id="resultArea" class="result-box">
                    <p style="color: #666; text-align: center;">执行结果将显示在这里...</p>
                </div>

                <h2 style="margin-top: 20px;">📝 系统日志</h2>

                <div id="logContainer" style="max-height: 300px; overflow-y: auto;">
                    <!-- 日志动态生成 -->
                </div>
            </div>
        </div>
    </div>

    <script>
        // 状态管理
        let messages = [];

        // 标签页切换
        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(tab => {
                if (tab.textContent.toLowerCase().includes(tabName)) {
                    tab.classList.add('active');
                }
            });

            document.getElementById('tab-control').style.display = tabName === 'control' ? 'block' : 'none';
            document.getElementById('tab-llm').style.display = tabName === 'llm' ? 'block' : 'none';
            document.getElementById('tab-status').style.display = tabName === 'status' ? 'block' : 'none';

            if (tabName === 'status') {
                updateAgentList();
            }
        }

        // 更新Agent信息
        function updateAgentInfo() {
            const agentType = document.getElementById('agentType').value;
            const actionType = document.getElementById('actionType');

            // 根据Agent类型更新操作选项
            const actions = {
                'task_planner': ['generate_text', 'query_knowledge'],
                'knowledge': ['query_knowledge', 'validate_content', 'search_web'],
                'drafting': ['generate_text', 'validate_content'],
                'review': ['validate_content', 'query_knowledge'],
                'version': ['generate_text'],
                'member': ['query_knowledge']
            };

            actionType.innerHTML = actions[agentType].map(action =>
                `<option value="${action}">${action}</option>`
            ).join('');
        }

        // 执行Agent任务
        async function executeAgent() {
            const agentType = document.getElementById('agentType').value;
            const actionType = document.getElementById('actionType').value;
            const paramsText = document.getElementById('paramsInput').value;

            try {
                const params = paramsText ? JSON.parse(paramsText) : {};

                addLog(`执行Agent: ${agentType}, 操作: ${actionType}`, 'success');
                addChatMessage('user', `执行 ${agentType}.${actionType}`);

                const response = await fetch('/api/agent/execute', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        agent_type: agentType,
                        action: actionType,
                        params: params,
                        context: {}
                    })
                });

                const result = await response.json();

                if (result.success) {
                    addLog(`执行成功: ${result.message}`, 'success');
                    displayResult(result);
                    addChatMessage('assistant', JSON.stringify(result.data, null, 2));
                } else {
                    addLog(`执行失败: ${result.message}`, 'error');
                    displayResult(result);
                }
            } catch (error) {
                addLog(`错误: ${error.message}`, 'error');
                displayResult({success: false, error: error.message});
            }
        }

        // 大模型对话
        async function chatWithLLM() {
            const systemPrompt = document.getElementById('systemPrompt').value;
            const userMessage = document.getElementById('userMessage').value;
            const temperature = parseFloat(document.getElementById('temperature').value);

            if (!userMessage.trim()) {
                alert('请输入消息');
                return;
            }

            try {
                addLog(`LLM对话: ${userMessage.substring(0, 50)}...`, 'success');
                addChatMessage('user', userMessage);

                const messages = [];
                if (systemPrompt) {
                    messages.push({role: 'system', content: systemPrompt});
                }
                messages.push({role: 'user', content: userMessage});

                const response = await fetch('/api/llm/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        messages: messages,
                        temperature: temperature
                    })
                });

                const result = await response.json();

                if (result.success) {
                    addLog(`LLM响应成功，长度: ${result.content.length}`, 'success');
                    addChatMessage('assistant', result.content);
                    displayResult(result);
                } else {
                    addLog(`LLM响应失败: ${result.error}`, 'error');
                    addChatMessage('assistant', `错误: ${result.error}`);
                }
            } catch (error) {
                addLog(`错误: ${error.message}`, 'error');
            }
        }

        // 发送消息
        function sendMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();

            if (!message) return;

            addChatMessage('user', message);
            input.value = '';

            // 简单回复（实际应调用Agent）
            setTimeout(() => {
                addChatMessage('assistant', `收到消息: "${message}"，系统正在处理...`);
            }, 500);
        }

        // 添加聊天消息
        function addChatMessage(role, content) {
            const container = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${role}`;
            messageDiv.innerHTML = content.replace(/\n/g, '<br>');
            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
        }

        // 添加日志
        function addLog(message, type = 'info') {
            const container = document.getElementById('logContainer');
            const logDiv = document.createElement('div');
            logDiv.className = `log-entry ${type}`;

            const timestamp = new Date().toLocaleTimeString();
            logDiv.innerHTML = `[${timestamp}] ${message}`;

            container.insertBefore(logDiv, container.firstChild);

            // 限制日志数量
            while (container.children.length > 50) {
                container.removeChild(container.lastChild);
            }
        }

        // 显示结果
        function displayResult(result) {
            const area = document.getElementById('resultArea');
            area.innerHTML = `<pre style="white-space: pre-wrap; word-wrap: break-word;">${JSON.stringify(result, null, 2)}</pre>`;
        }

        // 清空对话
        function clearChat() {
            document.getElementById('chatContainer').innerHTML = '';
            addLog('对话已清空');
        }

        // 快速测试
        async function quickTest() {
            addLog('开始快速测试...', 'success');

            try {
                // 测试LLM
                const llmResponse = await fetch('/api/llm/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        messages: [{role: 'user', content: '你好，请介绍一下自己'}]
                    })
                });
                const llmResult = await llmResponse.json();

                if (llmResult.success) {
                    addLog('LLM测试成功', 'success');
                } else {
                    addLog(`LLM测试失败: ${llmResult.error}`, 'error');
                }

                // 测试Agent
                const agentResponse = await fetch('/api/agent/execute', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        agent_type: 'knowledge',
                        action: 'query_knowledge',
                        params: {query: '测试'},
                        context: {}
                    })
                });
                const agentResult = await agentResponse.json();

                if (agentResult.success) {
                    addLog('Agent测试成功', 'success');
                } else {
                    addLog(`Agent测试失败: ${agentResult.message}`, 'error');
                }

                displayResult({
                    llm: llmResult,
                    agent: agentResult,
                    status: 'quick_test_completed'
                });

            } catch (error) {
                addLog(`快速测试失败: ${error.message}`, 'error');
            }
        }

        // 更新Agent列表
        function updateAgentList() {
            const container = document.getElementById('agentList');

            const agents = [
                {name: 'TaskPlanner', type: 'task_planner', status: 'ready'},
                {name: 'KnowledgeAgent', type: 'knowledge', status: 'ready'},
                {name: 'DraftingAgent', type: 'drafting', status: 'ready'},
                {name: 'ReviewAgent', type: 'review', status: 'ready'},
                {name: 'VersionAgent', type: 'version', status: 'ready'},
                {name: 'MemberAgent', type: 'member', status: 'ready'}
            ];

            container.innerHTML = agents.map(agent => `
                <div class="agent-card">
                    <h3>${agent.name}</h3>
                    <p>类型: ${agent.type}</p>
                    <p>状态: <span class="status-badge status-success">就绪</span></p>
                </div>
            `).join('');
        }

        // 初始化
        document.addEventListener('DOMContentLoaded', () => {
            addLog('调试界面已加载', 'success');
            updateAgentInfo();
        });
    </script>
</body>
</html>
"""


# ============ API路由 ============

@app.get("/", response_class=HTMLResponse)
async def root():
    """主页面"""
    return HTMLResponse(content=HTML_TEMPLATE)


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "agents": {
            "dispatcher": "ready",
            "task_planner": "ready",
            "knowledge": "ready",
            "drafting": "ready",
            "review": "ready",
            "version": "ready",
            "member": "ready"
        }
    }


@app.post("/api/llm/chat")
async def llm_chat(request: ChatRequest):
    """大模型对话接口"""
    try:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]

        llm_service = get_llm_service()
        result = await llm_service.chat(
            messages=messages,
            temperature=request.temperature
        )

        if result["success"]:
            return {
                "success": True,
                "content": result["content"],
                "usage": result.get("usage", {}),
                "model": result.get("model")
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "未知错误"),
                "message": result.get("message", "调用失败")
            }

    except Exception as e:
        logger.error(f"LLM对话异常: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "对话异常"
        }


@app.post("/api/agent/execute")
async def agent_execute(request: AgentRequest):
    """执行Agent任务"""
    try:
        # 创建任务
        task = AgentTask(
            task_id=f"debug_{hash(str(request.agent_type + request.action))}",
            agent_type=request.agent_type,
            action=request.action,
            params=request.params,
            context=request.context,
            priority=1,
            timeout=120
        )

        # 获取调度器
        dispatcher = get_dispatcher()

        # 执行任务
        result = await dispatcher.invoke_agent(task)

        logger.info(f"Agent执行完成: {request.agent_type}.{request.action}, 状态: {result.status}")

        return {
            "success": result.status == "success",
            "message": result.message,
            "data": result.data,
            "agent_type": request.agent_type,
            "action": request.action,
            "execution_time": getattr(result, 'execution_time', None)
        }

    except Exception as e:
        logger.error(f"Agent执行异常: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"执行异常: {str(e)}"
        }


@app.get("/api/agents/status")
async def agents_status():
    """获取所有Agent状态"""
    try:
        dispatcher = get_dispatcher()
        state = dispatcher.get_state()

        return {
            "success": True,
            "current_phase": getattr(state, 'current_phase', 'unknown'),
            "task_id": getattr(state, 'task_id', 'unknown'),
            "agents": {
                "task_planner": "ready",
                "knowledge": "ready",
                "drafting": "ready",
                "review": "ready",
                "version": "ready",
                "member": "ready"
            }
        }
    except Exception as e:
        logger.error(f"获取状态异常: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/agent/test")
async def agent_test(agent_type: str = "knowledge"):
    """快速测试Agent"""
    try:
        # 创建测试任务
        task = AgentTask(
            task_id="test_quick",
            agent_type=agent_type,
            action="query_knowledge",
            params={"query": "测试查询"},
            context={}
        )

        dispatcher = get_dispatcher()
        result = await dispatcher.invoke_agent(task)

        return {
            "success": result.status == "success",
            "result": result
        }

    except Exception as e:
        logger.error(f"测试异常: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


# ============ 启动服务 ============

if __name__ == "__main__":
    import uvicorn

    print("""
    ╔═════════════════════════════════════════════════╗
    ║                                                           ║
    ║        县志Agent调试界面启动中...                     ║
    ║                                                           ║
    ║        访问地址: http://localhost:8000                ║
    ║        API文档: http://localhost:8000/docs                ║
    ║                                                           ║
    ║        注意: 这是临时调试界面，实际项目中不需要              ║
    ║                                                           ║
    ╚═════════════════════════════════════════════════╝
    """)

    uvicorn.run(
        app,
        host="0.0.0.0.0",
        port=8000,
        log_level="info"
    )
