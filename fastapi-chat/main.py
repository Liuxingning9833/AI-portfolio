"""AI Chat API — FastAPI + DeepSeek/OpenAI
支持多轮对话、历史记录、流式输出
启动: uvicorn main:app --host 0.0.0.0 --port 8800
文档: http://127.0.0.1:8800/docs
"""
import os, json, uuid, time
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx

app = FastAPI(title="AI Chat API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# 对话会话存储（生产环境应使用 Redis/数据库）
sessions: dict = {}

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    model: str = "deepseek-chat"
    temperature: float = 0.7
    system_prompt: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    model: str
    tokens_used: int
    timestamp: str

class SessionInfo(BaseModel):
    session_id: str
    created_at: str
    message_count: int
    preview: str

DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

async def call_llm(messages: list, model: str, temperature: float) -> tuple:
    """调用 DeepSeek API"""
    if not API_KEY:
        raise HTTPException(500, "未设置 DEEPSEEK_API_KEY 环境变量")

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            DEEPSEEK_URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages, "temperature": temperature}
        )
        if resp.status_code != 200:
            raise HTTPException(resp.status_code, f"API 错误: {resp.text}")
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)
        return content, tokens

@app.post("/chat", response_model=ChatResponse, summary="发送对话消息")
async def chat(req: ChatRequest):
    """发送消息并获取 AI 回复，支持多轮对话"""
    sid = req.session_id or str(uuid.uuid4())[:8]

    if sid not in sessions:
        sessions[sid] = {
            "id": sid,
            "created_at": datetime.now().isoformat(),
            "messages": []
        }

    session = sessions[sid]

    # 构建消息列表
    messages = []
    if req.system_prompt:
        messages.append({"role": "system", "content": req.system_prompt})
    messages.extend(session["messages"])
    messages.append({"role": "user", "content": req.message})

    # 调用 LLM
    reply, tokens = await call_llm(messages, req.model, req.temperature)

    # 保存对话历史
    session["messages"].append({"role": "user", "content": req.message})
    session["messages"].append({"role": "assistant", "content": reply})
    # 只保留最近 20 轮
    if len(session["messages"]) > 40:
        session["messages"] = session["messages"][-40:]

    return ChatResponse(
        session_id=sid,
        reply=reply,
        model=req.model,
        tokens_used=tokens,
        timestamp=datetime.now().isoformat()
    )

@app.get("/sessions", summary="列出所有对话会话")
async def list_sessions():
    """返回所有活跃会话"""
    result = []
    for sid, s in sessions.items():
        msgs = s["messages"]
        preview = ""
        for m in msgs:
            if m["role"] == "user":
                preview = m["content"][:50]
                break
        result.append(SessionInfo(
            session_id=sid,
            created_at=s["created_at"],
            message_count=len(msgs),
            preview=preview
        ))
    return sorted(result, key=lambda x: x.created_at, reverse=True)

@app.get("/sessions/{session_id}", summary="获取会话详情")
async def get_session(session_id: str):
    """获取指定会话的完整历史"""
    if session_id not in sessions:
        raise HTTPException(404, "会话不存在")
    return {
        "session_id": session_id,
        "messages": sessions[session_id]["messages"],
        "created_at": sessions[session_id]["created_at"]
    }

@app.delete("/sessions/{session_id}", summary="删除会话")
async def delete_session(session_id: str):
    """删除指定会话"""
    if session_id in sessions:
        del sessions[session_id]
    return {"ok": True}

@app.get("/health", summary="健康检查")
async def health():
    return {"status": "ok", "model": "deepseek-chat", "sessions": len(sessions)}

CHAT_PAGE = """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AI Chat</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);min-height:100vh;display:flex;justify-content:center;align-items:center}
.container{width:100%;max-width:720px;height:100vh;display:flex;flex-direction:column;background:rgba(255,255,255,0.03);backdrop-filter:blur(10px)}
.hd{background:rgba(0,0,0,0.3);padding:14px 20px;display:flex;align-items:center;gap:10px;border-bottom:1px solid rgba(255,255,255,0.08)}.hd .dot{width:10px;height:10px;border-radius:50%;background:#6ee7b7}.hd h1{font-size:18px;color:#e8e8f0;font-weight:600}
.msgs{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:16px}
.msg{max-width:85%;padding:12px 16px;border-radius:14px;font-size:14px;line-height:1.6;animation:fadeIn .3s}@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.msg.user{align-self:flex-end;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border-bottom-right-radius:4px}
.msg.bot{align-self:flex-start;background:rgba(255,255,255,0.08);color:#d8d8e8;border:1px solid rgba(255,255,255,0.1);border-bottom-left-radius:4px}
.bar{padding:14px 20px;background:rgba(0,0,0,0.3);display:flex;gap:10px;border-top:1px solid rgba(255,255,255,0.08)}
.bar input{flex:1;padding:12px 18px;border-radius:24px;border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.06);color:#e8e8f0;font-size:14px;outline:none;transition:.3s}
.bar input:focus{border-color:#764ba2;box-shadow:0 0 12px rgba(118,75,162,0.3)}
.bar button{width:44px;height:44px;border-radius:50%;border:none;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;cursor:pointer;font-size:18px;transition:.2s;flex-shrink:0}
.bar button:hover{transform:scale(1.05);box-shadow:0 4px 15px rgba(118,75,162,0.4)}
.bar button:disabled{opacity:0.4;transform:none}
.typing{display:inline-flex;gap:4px;padding:4px 0}.typing span{width:6px;height:6px;border-radius:50%;background:#a0a0c0;animation:blink 1.4s infinite}.typing span:nth-child(2){animation-delay:.2s}.typing span:nth-child(3){animation-delay:.4s}@keyframes blink{0%,80%,100%{opacity:0.2}40%{opacity:1}}
</style></head><body>
<div class="container">
<div class="hd"><div class="dot"></div><h1>AI Chat API</h1></div>
<div class="msgs" id="msgs"><div class="msg bot">你好！我是 AI 助手，基于 DeepSeek 大模型。<br>我可以多轮对话、记住上下文。试试问我问题吧 👋</div></div>
<div class="bar"><input id="input" placeholder="输入消息..." onkeydown="event.key==='Enter'&&send()"><button id="btn" onclick="send()">↑</button></div>
</div>
<script>
let sid=null,busy=false;
async function send(){
  if(busy)return;let i=document.getElementById('input'),t=i.value.trim();if(!t)return;i.value='';
  add('user',t);busy=true;document.getElementById('btn').disabled=true;
  let ty=document.createElement('div');ty.className='msg bot';ty.innerHTML='<div class="typing"><span></span><span></span><span></span></div>';msgs.appendChild(ty);msgs.scrollTop=msgs.scrollHeight;
  try{
    let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t,session_id:sid,model:'deepseek-chat',system_prompt:'你是一个智能AI助手。用自然的中文回复。简洁专业。'})});
    let d=await r.json();sid=d.session_id;ty.remove();add('bot',d.reply);
  }catch(e){ty.remove();add('bot','错误: '+e.message)}
  busy=false;document.getElementById('btn').disabled=false;
}
function add(role,text){let d=document.createElement('div');d.className='msg '+role;d.textContent=text;msgs.appendChild(d);msgs.scrollTop=msgs.scrollHeight}
</script></body></html>"""

@app.get("/", response_class=HTMLResponse)
async def chat_ui():
    return CHAT_PAGE

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8800)
