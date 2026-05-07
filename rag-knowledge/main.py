"""Local Knowledge Base RAG - FastAPI + DeepSeek
Start: uvicorn main:app --host 127.0.0.1 --port 8851
"""
import os, tempfile, re, json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

app = FastAPI(title="RAG Knowledge Base")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")
DATA_FILE = "./knowledge_data.json"
documents = []  # [{source, chunks: [{text, index}]}]

# Load saved data on startup
try:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, encoding="utf-8") as f:
            documents = json.load(f)
except: pass

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False)

def chunk_text(text, size=400):
    sentences = re.split(r'(?<=[。！？\n])', text)
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) > size and current:
            chunks.append(current.strip())
            current = s
        else:
            current += s
    if current.strip(): chunks.append(current.strip())
    return chunks or [text[:size]]

def search_chunks(query, top_k=3):
    """Simple keyword overlap search - fast, no GPU needed"""
    keywords = set(query.lower())
    scored = []
    for doc in documents:
        for chunk in doc.get("chunks", []):
            text = chunk.get("text", "")
            # Count keyword overlap
            score = sum(1 for k in keywords if k in text.lower())
            if score > 0:
                scored.append((score, doc["source"], text[:300]))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [{"source": s[1], "preview": s[2]} for s in scored[:top_k]]

@app.get("/", response_class=HTMLResponse)
async def home():
    ui_path = os.path.join(os.path.dirname(__file__), "ui.html")
    return open(ui_path, encoding="utf-8").read()

@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)):
    global documents
    count = 0
    for f in files:
        content = (await f.read()).decode("utf-8", errors="replace")
        chunks = [{"text": c, "index": i} for i, c in enumerate(chunk_text(content))]
        documents.append({"source": f.filename, "chunks": chunks})
        count += len(chunks)
    save_data()
    return {"ok": True, "documents": len(files), "chunks": count}

@app.post("/query")
async def query(q: str = Form(...)):
    if not documents:
        raise HTTPException(400, "Please upload documents first")

    sources = search_chunks(q, top_k=3)
    if not sources:
        return {"answer": "No relevant content found in the uploaded documents.", "sources": []}

    ctx = "\n\n".join([f"[{s['source']}]\n{s['preview']}" for s in sources])

    prompt = f"""Answer the question based ONLY on the provided documents.
If the answer cannot be found, say "Not found in documents".

[Documents]
{ctx}

[Question]
{q}

[Answer]"""

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    answer = resp.choices[0].message.content
    return {"answer": answer, "sources": sources}

if __name__ == "__main__":
    import uvicorn; uvicorn.run(app, host="127.0.0.1", port=8851)
