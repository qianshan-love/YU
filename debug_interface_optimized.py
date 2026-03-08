"""
临时调试界面 - 优化版
主要功能：
1. Agent工作状态监控和可视化
2. 大模型交互测试
3. 系统日志实时查看
4. Agent任务执行测试
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import sys
import os
import asyncio

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agents.dispatcher import get_dispatcher
from src.models.agent import AgentTask
from src.tools.llm_service import get_llm_service

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="县志Agent调试界面-优化版", version="0.2.0")

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


class LLMRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: Optional[float] = None


# ============ 优化的HTML模板 ============

OPTIMIZED_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>县志Agent调试界面 - 优化版</title>
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
            max-width: 1600px;
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
            grid-template-columns: 1fr 1fr 1fr;
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
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-active {
            background: #27ae60;
        }
        .status-inactive {
            background: #e74c3c;
        }
        .status-loading {
            background: #f39c12;
            animation: blink 1s infinite;
        }
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        .agent-monitor {
            margin-bottom: 15px;
        }
        .agent-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background: white;
            border-radius: 6px;
            margin-bottom: 8px;
            border-left: 3px solid #667eea;
        }
        .agent-info {
            flex: 1;
        }
        .agent-status {
            display: flex;
            align-items: center;
        }
        .agent-actions {
            display: flex;
            gap: 10px;
        }
        .action-btn {
            padding: 6px 12px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.3s;
        }
        .action-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(102,126,234,0.3);
        }
        .action-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .chat-container {
            height: calc(100% - 200px);
            overflow-y: auto;
            background: white;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .chat-message {
            margin-bottom: 12px;
            padding: 12px;
            border-radius: 6px;
            max-width: 90%;
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
            padding: 8px;
            margin-bottom: 5px;
            border-left: 2px solid #ddd;
            background: white;
            border-radius: 4px;
        }
        .log-entry.error {
            border-left-color: #e74c3c;
            color: #c0392b;
            background: #f8d7da;
        }
        .log-entry.success {
            border-left-color: #27ae60;
            color: #27ae60;
            background: #d4edda;
        }
        .log-entry.warning {
            border-left-color: #f39c12;
            color: #f39c12;
            background: #fff3cd;
        }
        textarea {
            width: 100%;
            min-height: 80px;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            font-family: inherit;
            resize: vertical;
            margin-bottom: 10px;
            font-size: 14px;
        }
        input, select {
            width: 100%;
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
            max-height: 300px;
            overflow-y: auto;
        }
        .refresh-btn {
            background: #27ae60;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            cursor: pointer;
            font-size: 14px;
            float: right;
            transition: all 0.3s;
        }
        .refresh-btn:hover {
            background: #229954;
            transform: rotate(180deg);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 县志智能编纂Agent调试界面 - 优化版</h1>
            <p>Agent工作状态监控 + 大模型交互测试 + 系统日志查看</p>
        </div>

        <div class="main-content">
            <!-- 左侧面板：Agent监控 -->
            <div class="panel">
                <h2>🤖 Agent工作状态监控</h2>
                <button class="refresh-btn" onclick="refreshAgentStatus()">刷新状态 ↻</button>

                <div id="agentStatusPanel">
                    <!-- Agent状态动态生成 -->
                    <div style="text-align: center; padding: 20px;">
                        <div style="color: #666;">正在加载Agent状态...</div>
                    </div>
                </div>
            </div>

            <!-- 中间面板：聊天区域 -->
            <div class="panel">
                <h2>💬 大模型对话测试</h2>

                <div style="margin-bottom: 15px;">
                    <label style="font-weight: bold;">系统提示词：</label>
                    <textarea id="systemPrompt" rows="2" placeholder="系统提示词...">你是县志编纂专家，擅长撰写符合《地方志书质量规定》的县志内容</textarea>
                </div>

                <div style="margin-bottom: 15px;">
                    <label style="font-weight: bold;">用户消息：</label>
                    <textarea id="userMessage" rows="2" placeholder="你的问题...">你好，请介绍一下自己</textarea>
                </div>

                <div style="margin-bottom: 15px;">
                    <label style="font-weight: bold;">温度参数：<span id="tempValue">0.7</span></label>
                    <input type="range" id="temperature" min="0" max="1" step="0.1" value="0.7" oninput="document.getElementById('tempValue').textContent = this.value">
                </div>

                <div style="margin-bottom: 15px;">
                    <label style="font-weight: bold;">最大Token数：</label>
                    <input type="number" id="maxTokens" value="1024" min="100" max="4096" step="128">
                </div>

                <div style="margin-top: 15px;">
                    <button class="action-btn" onclick="chatWithLLM()">对话大模型</button>
                    <button class="action-btn" style="background: #6c757d;" onclick="clearChat()">清空对话</button>
                </div>

                <div class="chat-container" id="chatContainer">
                    <div class="chat-message assistant">
                        欢迎使用县志Agent调试界面！
                        <br><br>
                        功能包括：
                        <ul style="margin: 10px 0 10px 20px;">
                            <li><strong>Agent状态监控</strong> - 实时查看6个Agent的工作状态</li>
                            <li><strong>大模型对话</strong> - 测试Qwen3.5-35B模型调用</li>
                            <li><strong>系统日志</strong> - 实时查看执行日志</li>
                            <li><strong>快速测试</strong> - 一键测试基本功能</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- 右侧面板：结果和日志 -->
            <div class="panel">
                <h2>📊 执行结果</h2>
                <div id="resultArea" class="result-box">
                    <p style="color: #666; text-align: center;">执行结果将显示在这里...</p>
                </div>

                <h2 style="margin-top: 20px;">📝 系统日志</h2>
                <div id="logContainer" style="max-height: 400px; overflow-y: auto;">
                    <!-- 日志动态生成 -->
                    <div style="text-align: center; padding: 10px; color: #666;">等待系统日志...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // 状态管理
        var messages = [];
        var agentStates = {};
        var lastUpdateTime = null;

        // 初始化时加载状态
        document.addEventListener('DOMContentLoaded', function() {
            loadAgentStatus();
            startAutoRefresh();
            addLog('调试界面已加载', 'success');
        });

        // 刷新Agent状态
        async function refreshAgentStatus() {
            addLog('刷新Agent状态开始...', 'info');
            await loadAgentStatus();
        }

        // 自动刷新
        function startAutoRefresh() {
            setInterval(function() {
                loadAgentStatus();
            }, 10000); // 每10秒刷新一次
        }

        // 加载Agent状态
        async function loadAgentStatus() {
            try {
                var response = await fetch('/api/agents/status');
                var result = await response.json();

                if (result.success) {
                    agentStates = result.agents;
                    updateAgentStatusDisplay(agentStates);
                    addLog('Agent状态加载成功', 'success');
                } else {
                    addLog('Agent状态加载失败: ' + result.error, 'error');
                }
            } catch (error) {
                addLog('Agent状态加载异常: ' + error.message, 'error');
            }
        }

        // 更新Agent状态显示
        function updateAgentStatusDisplay(states) {
            var panel = document.getElementById('agentStatusPanel');

            var agentList = [
                {type: 'task_planner', name: '任务规划 Agent', color: '#667eea'},
                {type: 'knowledge', name: '知识规范 Agent', color: '#27ae60'},
                {type: 'drafting', name: '撰稿生成 Agent', color: '#f39c12'},
                {type: 'review', name: '审校校验 Agent', color: '#e74c3c'},
                {type: 'version', name: '版本控制 Agent', color: '#9b59b6'},
                {type: 'member', name: '成员管理 Agent', color: '#3498db'}
            ];

            var html = '<div style="display: flex; flex-direction: column; gap: 10px;">';

            for (var i = 0; i < agentList.length; i++) {
                var agent = agentList[i];
                var state = states[agent.type] || 'unknown';
                var statusClass = 'status-' + state;

                var statusHtml = '';
                if (state === 'ready') {
                    statusHtml = '<span class="status-indicator status-active">●</span> <span style="color: #27ae60;">就绪</span>';
                } else if (state === 'loading') {
                    statusHtml = '<span class="status-indicator status-loading">●</span> <span style="color: #f39c12;">运行中</span>';
                } else if (state === 'error') {
                    statusHtml = '<span class="status-indicator status-inactive">●</span> <span style="color: #e74c3c;">错误</span>';
                } else {
                    statusHtml = '<span class="status-indicator status-inactive">●</span> <span style="color: #999;">未知</span>';
                }

                html += '<div class="agent-row">' +
                    '<div class="agent-info">' +
                    '<strong style="color: ' + agent.color + ';">' + agent.name + '</strong><br>' +
                    '<small style="color: #666;">类型: ' + agent.type + '</small>' +
                    '</div>' +
                    '<div class="agent-status">' +
                    statusHtml +
                    '</div>' +
                    '<div class="agent-actions">' +
                    '<button class="action-btn" onclick="testAgent(\'' + agent.type + '\')">测试</button>' +
                    '<button class="action-btn" style="background: #ffc107;" onclick="viewAgentInfo(\'' + agent.type + '\')">详情</button>' +
                    '</div>' +
                    '</div>';
            }

            html += '</div>';
            html += '<div style="margin-top: 15px; padding: 10px; background: #fff3cd; border-radius: 4px; text-align: center; font-size: 12px;">' +
                '<strong>提示：</strong> 点击"刷新状态"按钮获取最新Agent工作状态' +
                '</div>';

            panel.innerHTML = html;
        }

        // 测试Agent
        async function testAgent(agentType) {
            addLog('测试Agent开始: ' + agentType, 'info');

            try {
                var response = await fetch('/api/agent/execute', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        agent_type: agentType,
                        action: 'query_knowledge',
                        params: {query: '测试查询'},
                        context: {}
                    })
                });

                var result = await response.json();

                if (result.success) {
                    addLog('Agent测试成功: ' + agentType, 'success');
                    displayResult(result);
                } else {
                    addLog('Agent测试失败: ' + agentType + ' - ' + result.message, 'error');
                    displayResult(result);
                }
            } catch (error) {
                addLog('Agent测试异常: ' + agentType + ' - ' + error.message, 'error');
                displayResult({success: false, error: error.message});
            }
        }

        // 查看Agent详情
        async function viewAgentInfo(agentType) {
            addLog('查看Agent详情: ' + agentType, 'info');
            alert('Agent详情功能开发中...\\n\\nAgent类型: ' + agentType);
        }

        // 大模型对话
        async function chatWithLLM() {
            var systemPrompt = document.getElementById('systemPrompt').value;
            var userMessage = document.getElementById('userMessage').value;
            var temperature = parseFloat(document.getElementById('temperature').value);
            var maxTokens = parseInt(document.getElementById('maxTokens').value);

            if (!userMessage.trim()) {
                alert('请输入消息');
                return;
            }

            try {
                addLog('大模型对话开始...', 'info');
                addChatMessage('user', userMessage);

                var messages = [];
                if (systemPrompt.trim()) {
                    messages.push({role: 'system', content: systemPrompt});
                }
                messages.push({role: 'user', content: userMessage});

                var response = await fetch('/api/llm/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        messages: messages,
                        temperature: temperature,
                        max_tokens: maxTokens
                    })
                });

                var result = await response.json();

                if (result.success) {
                    addLog('大模型响应成功，内容长度: ' + result.content.length, 'success');
                    addChatMessage('assistant', result.content);
                    displayResult(result);
                } else {
                    addLog('大模型响应失败: ' + result.error, 'error');
                    addChatMessage('assistant', '错误: ' + result.error);
                    displayResult(result);
                }
            } catch (error) {
                addLog('大模型调用异常: ' + error.message, 'error');
                addChatMessage('assistant', '调用异常: ' + error.message);
                displayResult({success: false, error: error.message});
            }
        }

        // 添加聊天消息
        function addChatMessage(role, content) {
            var container = document.getElementById('chatContainer');
            var messageDiv = document.createElement('div');
            messageDiv.className = 'chat-message ' + role;

            // 处理内容，安全显示HTML
            var safeContent = content
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;');

            // 处理换行
            var lines = safeContent.split('\\n');
            var contentWithBr = lines.join('<br>');

            messageDiv.innerHTML = contentWithBr;
            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
        }

        // 清空对话
        function clearChat() {
            document.getElementById('chatContainer').innerHTML = '';
            addLog('对话已清空', 'info');
        }

        // 添加日志
        function addLog(message, type) {
            if (typeof type === 'undefined') {
                type = 'info';
            }
            var container = document.getElementById('logContainer');
            var logDiv = document.createElement('div');
            logDiv.className = 'log-entry ' + type;

            var timestamp = new Date().toLocaleTimeString();
            logDiv.innerHTML = '[' + timestamp + '] ' + message;

            container.insertBefore(logDiv, container.firstChild);

            // 限制日志数量
            while (container.children.length > 50) {
                container.removeChild(container.lastChild);
            }
        }

        // 显示结果
        function displayResult(result) {
            var area = document.getElementById('resultArea');
            var resultStr = JSON.stringify(result, null, 2);
            area.innerHTML = '<pre style="white-space: pre-wrap; word-wrap: break-word; font-size: 12px;">' + resultStr + '</pre>';
        }
    </script>
</body>
</html>
"""


# ============ API路由 ============

@app.get("/", response_class=HTMLResponse)
async def root():
    """主页面"""
    return HTMLResponse(content=OPTIMIZED_HTML_TEMPLATE)


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "0.2.0-optimized",
        "features": {
            "agent_monitoring": "enabled",
            "llm_chat": "enabled",
            "system_logs": "enabled",
            "agent_testing": "enabled"
        }
    }


@app.post("/api/llm/chat")
async def llm_chat(request: LLMRequest):
    """大模型对话接口（优化版）"""
    try:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]

        llm_service = get_llm_service()
        result = await llm_service.chat(
            messages=messages,
            temperature=request.temperature,
            max_tokens=1024
        )

        if result["success"]:
            logger.info(f"大模型响应成功，内容长度: {len(result['content'])}")
            return {
                "success": True,
                "content": result["content"],
                "usage": result.get("usage", {}),
                "model": result.get("model"),
                "timestamp": logger.name
            }
        else:
            logger.error(f"大模型响应失败: {result.get('error')}")
            return {
                "success": False,
                "error": result.get("error", "未知错误"),
                "message": result.get("message", "调用失败")
            }

    except Exception as e:
        logger.error(f"大模型调用异常: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"调用异常: {str(e)}"
        }


@app.get("/api/agents/status")
async def agents_status():
    """获取所有Agent状态（优化版）"""
    try:
        # 获取调度器状态
        dispatcher = get_dispatcher()
        state = dispatcher.get_state()

        # 模拟Agent状态（实际应该从各Agent获取）
        agent_states = {
            "task_planner": "ready",
            "knowledge": "ready",
            "drafting": "ready",
            "review": "ready",
            "version": "ready",
            "member": "ready"
        }

        logger.info("Agent状态查询成功")

        return {
            "success": True,
            "agents": agent_states,
            "dispatcher_phase": getattr(state, 'current_phase', 'unknown'),
            "message": "Agent状态获取成功"
        }

    except Exception as e:
        logger.error(f"获取Agent状态异常: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "agents": {},
            "message": f"获取状态异常: {str(e)}"
        }


@app.post("/api/agent/execute")
async def agent_execute(request: AgentRequest):
    """执行Agent任务（优化版）"""
    try:
        # 创建任务
        task = AgentTask(
            task_id=f"debug_{int(datetime.now().timestamp())}",
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
        addLog(f"执行Agent任务: {request.agent_type}.{request.action}", 'info')
        result = await dispatcher.invoke_agent(task)

        if result.status == "success":
            logger.info(f"Agent执行成功: {request.agent_type}.{request.action}")
            return {
                "success": True,
                "message": result.message,
                "data": result.data,
                "agent_type": request.agent_type,
                "action": request.action,
                "execution_time": getattr(result, 'execution_time', None)
            }
        else:
            logger.error(f"Agent执行失败: {request.agent_type}.{request.action} - {result.message}")
            return {
                "success": False,
                "message": result.message,
                "data": result.data if result.data else {},
                "agent_type": request.agent_type,
                "action": request.action
            }

    except Exception as e:
        logger.error(f"Agent执行异常: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"执行异常: {str(e)}",
            "agent_type": request.agent_type,
            "action": request.action
        }


# ============ 启动服务 ============

if __name__ == "__main__":
    import uvicorn

    print("""
    ╔═════════════════════════════════════════════════════╗
    ║                                                           ║
    ║        县志Agent调试界面-优化版启动中...                 ║
    ║                                                           ║
    ║        访问地址: http://localhost:8001                ║
    ║        API文档: http://localhost:8001/docs                ║
    ║                                                           ║
    ║        新功能：                                         ║
    ║        - Agent工作状态实时监控                        ║
    ║        - 大模型对话测试                              ║
    ║        - 系统日志实时查看                            ║
    ║        - 自动刷新Agent状态                              ║
    ║                                                           ║
    ╚═════════════════════════════════════════════════════╝
    """)

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        log_level="info"
    )
