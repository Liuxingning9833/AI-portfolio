"""AI Resume Helper — FastAPI + DeepSeek
启动: uvicorn main:app --host 127.0.0.1 --port 8850
"""
import os, json
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

app = FastAPI(title="AI Resume Helper")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")
SYSTEM = "你是杭州AI行业资深HR顾问。了解DeepSeek、阿里、字节等公司。问题简洁实用，给可操作建议。"

@app.get("/", response_class=HTMLResponse)
async def home():
    ui_path = os.path.join(os.path.dirname(__file__), "ui.html")
    return open(ui_path, encoding="utf-8").read()

@app.post("/optimize")
async def optimize(name: str = Form(""), target: str = Form(""), resume: str = Form("")):
    prompt = f"""优化以下简历，目标岗位「{target}」（杭州）。
要求: STAR法则重写经历、补充技能关键词、量化成果、500字内、添加技能/项目/证书板块。
求职者: {name}
原始简历: {resume}"""
    return streaming_response(prompt)

@app.post("/match")
async def match(skills: str = Form("")):
    prompt = f"""求职者技能: {skills}
目标城市: 杭州。推荐3-5个岗位（名称+薪资+匹配度），推荐3家公司，技能补强建议，下一步行动。"""
    return streaming_response(prompt)

@app.post("/interview")
async def interview(job: str = Form(""), question: str = Form("")):
    if question:
        prompt = f"求职者问: {question}\n以杭州AI行业面试官身份回答。"
    else:
        prompt = f"生成5道「{job}」面试题。每道标注考察点+评分标准+范例回答。考察实际能力而非背诵。"
    return streaming_response(prompt)

def streaming_response(prompt):
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role":"system","content":SYSTEM},{"role":"user","content":prompt}],
        temperature=0.7, stream=True
    )
    def gen():
        for chunk in resp:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    return StreamingResponse(gen(), media_type="text/plain")

UI = """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AI Resume Helper</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:linear-gradient(135deg,#0d1220,#1a1040,#0d1220);min-height:100vh;color:#d0d0e0}
.hd{background:rgba(0,0,0,0.4);padding:16px 24px;display:flex;align-items:center;gap:12px;border-bottom:1px solid rgba(255,255,255,0.08)}.hd h1{font-size:20px;font-weight:700;background:linear-gradient(135deg,#f59e0b,#ef4444,#ec4899);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.tabs{display:flex;gap:4px;padding:16px 24px 0;max-width:900px;margin:0 auto}
.tab{padding:8px 20px;border-radius:10px 10px 0 0;border:1px solid rgba(255,255,255,0.08);border-bottom:none;background:rgba(255,255,255,0.02);color:#8080a0;cursor:pointer;font-size:13px;transition:.2s}.tab.sel{background:rgba(255,255,255,0.06);color:#e0e0f0;border-color:rgba(255,255,255,0.15)}
.main{max-width:900px;margin:0 auto;padding:24px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:0 0 16px 16px}
.row{display:flex;gap:12px;margin-bottom:12px}
.row input{flex:1;padding:10px 14px;border-radius:10px;border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.04);color:#d0d0e0;font-size:13px;outline:none}.row input:focus{border-color:#ec4899}
textarea{width:100%;padding:12px 14px;border-radius:10px;border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.04);color:#d0d0e0;font-size:13px;resize:vertical;min-height:120px;outline:none;font-family:inherit;margin-bottom:12px}textarea:focus{border-color:#ec4899}
.btn{width:100%;padding:12px;border-radius:12px;border:none;background:linear-gradient(135deg,#f59e0b,#ef4444,#ec4899);color:#fff;cursor:pointer;font-size:14px;font-weight:600;transition:.2s}.btn:hover{transform:translateY(-1px);box-shadow:0 4px 20px rgba(236,72,153,0.3)}.btn:disabled{opacity:0.5}
.out{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:16px;margin-top:16px;line-height:1.7;white-space:pre-wrap;display:none;font-size:14px}
</style></head><body>
<div class="hd"><h1>AI Resume Helper</h1><span style="font-size:12px;color:#606080">Hangzhou AI Jobs</span></div>
<div class="tabs"><div class="tab sel" onclick="switchTab(0)">Resume Optimize</div><div class="tab" onclick="switchTab(1)">Job Match</div><div class="tab" onclick="switchTab(2)">Mock Interview</div></div>
<div class="main">
<div id="tab0">
<div class="row"><input id="name" placeholder="Your Name"><input id="target" placeholder="Target Job, e.g. AIGC Prompt Engineer"></div>
<textarea id="resume" placeholder="Paste your resume here..."></textarea>
<button class="btn" id="btn0" onclick="doPost('/optimize',{name:'name',target:'target',resume:'resume'},'out0','btn0')">Optimize Resume</button>
<div class="out" id="out0"></div>
</div>
<div id="tab1" style="display:none">
<textarea id="skills" placeholder="Your skills (one per line):&#10;Python&#10;Prompt Engineering&#10;FastAPI&#10;Video Editing..."></textarea>
<button class="btn" id="btn1" onclick="doPost('/match',{skills:'skills'},'out1','btn1')">Find Matching Jobs</button>
<div class="out" id="out1"></div>
</div>
<div id="tab2" style="display:none">
<div class="row"><input id="job" placeholder="Job Title, e.g. AI Application Engineer"><input id="iq" placeholder="Or ask a question directly"></div>
<button class="btn" id="btn2" onclick="doPost('/interview',{job:'job',question:'iq'},'out2','btn2')">Generate / Ask</button>
<div class="out" id="out2"></div>
</div>
</div>
<script>
let curTab=0;
function switchTab(i){curTab=i;for(let t=0;t<3;t++){document.getElementById('tab'+t).style.display=t===i?'block':'none';document.querySelectorAll('.tab')[t].classList.toggle('sel',t===i)}}
async function doPost(url,fields,outId,btnId){let d=new FormData();for(let[k,id]of Object.entries(fields)){d.append(k,document.getElementById(id).value)}document.getElementById(btnId).disabled=true;let o=document.getElementById(outId);o.style.display='block';o.textContent='';let r=await fetch(url,{method:'POST',body:d});let t=await r.text();o.textContent=t;document.getElementById(btnId).disabled=false}
</script></body></html>"""

if __name__ == "__main__":
    import uvicorn; uvicorn.run(app, host="127.0.0.1", port=8850)
