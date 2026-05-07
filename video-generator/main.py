"""AI Batch Video Script Generator - FastAPI + DeepSeek
Upload product info -> AI generates video scripts, shot lists, and prompts for video tools
Start: uvicorn main:app --host 127.0.0.1 --port 8862
"""
import os, json, csv, io, time, re
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel

app = FastAPI(title="AI Video Generator")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")
jobs = {}  # Track batch jobs

@app.get("/", response_class=HTMLResponse)
async def home():
    with open(os.path.join(os.path.dirname(__file__), "ui.html"), encoding="utf-8") as f:
        return f.read()

@app.post("/generate")
async def generate(product_name: str = Form(""), product_desc: str = Form(""), platform: str = Form("抖音"), style: str = Form("产品展示"), count: int = Form(1)):
    """Generate video scripts for a single product"""
    prompt = f"""你是专业短视频编导。为以下产品生成{count}条{platform}短视频脚本。

产品名称：{product_name}
产品描述：{product_desc}
视频风格：{style}
目标平台：{platform}

对每条视频，请严格按以下格式输出（用三个等号分隔每条）：

=== VIDEO 1 ===
标题：（10字以内吸引人的标题）
时长：15-30秒
画面脚本：
| 时间 | 画面 | 字幕/旁白 | 音效 |
| 0-3s | 产品特写 | 吸引注意力的话术 | 轻快BGM |
| 3-10s | 使用场景 | 核心卖点 | BGM |
| 10-25s | 效果展示 | 引导下单 | BGM+提示音 |
| 25-30s | logo+结尾 | 关注点赞 | BGM收尾 |
AI视频提示词：（用于即梦/可灵/豆包等工具生成视频画面的中文提示词）
拍摄建议：具体的拍摄/剪辑技巧

注意：每个VIDEO之间用 === VIDEO N === 分隔，脚本表格保持整齐。"""

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role":"user","content":prompt}],
        temperature=0.8
    )
    return {"result": resp.choices[0].message.content}

@app.post("/batch")
async def batch_generate(file: UploadFile = File(...), platform: str = Form("抖音"), style: str = Form("产品展示")):
    """Batch generate from CSV/Excel"""
    content = (await file.read()).decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(content))
    products = []
    for row in reader:
        name = row.get("product_name") or row.get("name") or next((v for k,v in row.items() if v), "Unknown")
        desc = row.get("product_desc") or row.get("description") or row.get("desc") or ""
        if name and name != "Unknown":
            products.append({"name": name.strip(), "desc": desc.strip()[:200]})

    if not products:
        return {"error": "No valid products found in CSV. Columns should be: product_name, description"}

    job_id = str(int(time.time()))
    jobs[job_id] = {"total": len(products), "done": 0, "results": [], "status": "running"}
    return {"job_id": job_id, "total": len(products), "products": products}

@app.post("/batch/{job_id}/process")
async def process_batch(job_id: str):
    """Process next item in batch job"""
    job = jobs.get(job_id)
    if not job:
        return {"error": "Job not found"}

    # This will be called per-item by the frontend
    return {"status": job["status"], "done": job["done"], "total": job["total"]}

@app.post("/batch/{job_id}/result")
async def save_batch_result(job_id: str, product_name: str = Form(""), result: str = Form("")):
    """Save result for a batch item"""
    job = jobs.get(job_id)
    if not job:
        return {"error": "Job not found"}
    job["results"].append({"product": product_name, "script": result})
    job["done"] = len(job["results"])
    if job["done"] >= job["total"]:
        job["status"] = "completed"
    return {"status": job["status"], "done": job["done"], "total": job["total"]}

@app.get("/batch/{job_id}")
async def get_batch_results(job_id: str):
    """Get all results for a batch job"""
    job = jobs.get(job_id)
    if not job:
        return {"error": "Job not found"}
    return job

@app.get("/export/{job_id}")
async def export_results(job_id: str):
    """Export batch results as text file"""
    job = jobs.get(job_id)
    if not job or not job["results"]:
        return {"error": "No results to export"}
    text = "AI Video Script Batch Export\n" + "="*50 + "\n\n"
    for r in job["results"]:
        text += f"Product: {r['product']}\n{r['script']}\n\n{'='*50}\n\n"
    return StreamingResponse(io.StringIO(text), media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=video_scripts_{job_id}.txt"})

if __name__ == "__main__":
    import uvicorn; uvicorn.run(app, host="127.0.0.1", port=8862)
