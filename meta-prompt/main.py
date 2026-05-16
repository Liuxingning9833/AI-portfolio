"""Meta Prompting: AI Prompt Coach - FastAPI + DeepSeek
Start: uvicorn main:app --host 127.0.0.1 --port 8864
"""
import os, json
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

app = FastAPI(title="Meta Prompting")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

COACH_SYSTEM = """You are a world-class Prompt Engineering Coach. Your job is to help users craft perfect prompts.

When given a rough prompt, you:
1. Analyze what the user really wants
2. Identify missing elements (context, format, constraints, role, examples)
3. Output an optimized prompt that is structured, clear, and effective
4. Explain your improvements

Always respond in Chinese. Be encouraging but professional like a coach."""

@app.get("/", response_class=HTMLResponse)
async def home():
    with open(os.path.join(os.path.dirname(__file__), "ui.html"), encoding="utf-8") as f:
        return f.read()

@app.post("/optimize")
async def optimize(
    prompt: str = Form(""),
    mode: str = Form("optimize"),
    audience: str = Form("通用"),
    style: str = Form("详细")
):
    if mode == "optimize":
        task = f"""用户想优化以下提示词，请帮它变成专业级 Prompt。

目标受众：{audience}
回复风格：{style}

原始提示词：
{prompt}

请严格按以下 JSON 格式输出（不要输出其他内容）：
{{"optimized":"优化后的完整提示词","score":评分1-10,"improvements":["改进点1","改进点2","改进点3"],"tips":"一句话教练建议"}}"""
    elif mode == "analyze":
        task = f"""请分析以下提示词的优缺点，给出改进建议。

原始提示词：
{prompt}

请严格按以下 JSON 格式输出：
{{"optimized":"分析后建议的优化版本","score":评分1-10,"improvements":["问题1","问题2","建议1","建议2"],"tips":"一句话教练建议"}}"""
    elif mode == "template":
        task = f"""用户想写一个关于以下主题的提示词。请为其生成一个专业的 Prompt 模板。

主题：{prompt}
目标受众：{audience}
回复风格：{style}

请严格按以下 JSON 格式输出：
{{"optimized":"生成的专业Prompt模板","score":8,"improvements":["这个模板包含了角色设定","包含了输出格式要求","包含了约束条件"],"tips":"根据实际需求调整方括号中的内容"}}"""

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": COACH_SYSTEM},
            {"role": "user", "content": task}
        ],
        temperature=0.7
    )
    content = resp.choices[0].message.content.strip()
    # Extract JSON from response
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]
    try:
        return json.loads(content)
    except:
        return {"optimized": content, "score": 7, "improvements": ["解析结果"], "tips": "点击复制使用优化后的提示词"}

if __name__ == "__main__":
    import uvicorn; uvicorn.run(app, host="127.0.0.1", port=8864)
