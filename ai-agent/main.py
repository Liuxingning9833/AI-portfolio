"""AI Agent - Reliable JSON-based tool calling
The agent outputs JSON to call tools, we execute them, feed results back.
Tools: web search (Bing), calculator, weather, Python runner, time
"""
import os, json, math, re, urllib.request, urllib.parse, subprocess, tempfile, sys, time as _time
from datetime import datetime
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

app = FastAPI(title="AI Agent")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

AGENT_PROMPT = """You are an AI assistant with tools. Always respond in Chinese.

AVAILABLE TOOLS:
1. fetch_url(url) - Fetch content from a URL and extract the main text (news, articles, docs)
2. calculator(expression) - Evaluate math (supports +-*/ ** sqrt sin cos log)
3. get_weather(city) - Get current weather for a city
4. run_python(code) - Execute Python code safely
5. get_time() - Get current date and time
6. video_summary(url) - Fetch a video page and extract title, description, and tags

RULES:
- When you need information, call tools. Do NOT guess.
- Output EXACTLY one valid JSON object per response, nothing else.
- To call a tool: {"action":"tool","tool":"<name>","args":{"param":"value"}}
- To answer: {"action":"answer","content":"<your response in Chinese>"}

EXAMPLES:
User: "What time is it? Calculate 123*456"
You: {"action":"tool","tool":"get_time","args":{}}
[system returns result]
You: {"action":"tool","tool":"calculator","args":{"expression":"123*456"}}
[system returns result]
You: {"action":"answer","content":"现在时间是X，123*456=56088"}

Call tools ONE AT A TIME. After each tool result, decide if you need more tools or can answer."""

def fetch_url(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        # Extract text
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<nav[^>]*>.*?</nav>', '', text, flags=re.DOTALL)
        text = re.sub(r'<footer[^>]*>.*?</footer>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'&[a-z]+;', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        # Take meaningful segments
        segs = [s.strip() for s in re.split(r'[。！？\n]', text) if len(s.strip()) > 15]
        return "\n".join(segs[:15]) if segs else text[:2000]
    except Exception as e:
        return f"Fetch failed: {str(e)[:100]}"

def calculator(expression=""):
    ns = {"__builtins__": {}, "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
          "tan": math.tan, "log": math.log, "abs": abs, "pow": pow, "pi": math.pi, "e": math.e}
    return str(eval(expression, ns))

def get_weather(city):
    try:
        url = f"https://wttr.in/{urllib.parse.quote(city)}?format=%C+%t+%w+%h"
        req = urllib.request.Request(url, headers={"User-Agent": "curl"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.read().decode().strip()
    except Exception as e:
        return f"Weather error: {str(e)[:100]}"

def run_python(code):
    for d in ["os.", "subprocess", "shutil", "sys.", "eval(", "exec(", "__import__", "open(", "file("]:
        if d in code: return f"Forbidden: {d}"
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
        f.write(code); tmp = f.name
    try:
        r = subprocess.run([sys.executable, tmp], capture_output=True, text=True, timeout=5)
        return (r.stdout or r.stderr or "(no output)")[:1000]
    finally:
        os.unlink(tmp)

def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S %A")

def video_summary(url):
    """Fetch video info - uses Bilibili/YouTube APIs for JS-rendered sites"""
    try:
        if not url.startswith("http"):
            url = "https://" + url

        # Special handling for Bilibili - use their public API
        bv_match = re.search(r'(BV[a-zA-Z0-9]{10})|(av\d+)', url)
        if bv_match:
            vid = bv_match.group(0)
            api_url = f"https://api.bilibili.com/x/web-interface/view?{('bvid' if vid.startswith('BV') else 'aid')}={vid}"
            req = urllib.request.Request(api_url, headers={
                "User-Agent": "Mozilla/5.0", "Referer": "https://www.bilibili.com"
            })
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read())["data"]
            return (
                f"Title: {data['title']}\n"
                f"Description: {data.get('desc','')[:500]}\n"
                f"Duration: {data['duration']} sec | "
                f"Views: {data['stat']['view']} | "
                f"Likes: {data['stat']['like']} | "
                f"Comments: {data['stat']['reply']}\n"
                f"Author: {data['owner']['name']} | "
                f"Tags: {data.get('tname','')}\n"
                f"URL: {url}"
            )
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        # Extract video metadata from common tags
        title = ""
        desc = ""
        tags = ""

        # Try <title>
        t = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
        if t: title = re.sub(r'<[^>]+>', '', t.group(1)).strip()

        # Try meta description (multiple patterns)
        for pat in [
            r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']',
            r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']description["\']',
        ]:
            d = re.search(pat, html)
            if d: desc = d.group(1)[:500]; break

        # Try meta keywords
        k = re.search(r'<meta[^>]*name=["\']keywords["\'][^>]*content=["\']([^"\']+)["\']', html)
        if k: tags = k.group(1)[:300]

        # Open Graph
        og_title = re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']+)["\']', html)
        og_desc = re.search(r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']+)["\']', html)

        # Try JSON-LD for video data
        jsonld = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL)
        extra = ""
        for ld in jsonld[:2]:
            try:
                data = json.loads(ld)
                if isinstance(data, dict):
                    name = data.get("name") or data.get("headline", "")
                    d2 = data.get("description", "")
                    if name and name not in title:
                        extra += f"\nJSON-LD Name: {name}"
                    if d2 and d2 not in desc:
                        extra += f"\nJSON-LD Desc: {d2[:300]}"
            except: pass

        return (
            f"Title: {og_title.group(1) if og_title else title}\n"
            f"Description: {og_desc.group(1) if og_desc else desc}\n"
            f"Tags: {tags}\n"
            f"{extra}"
        ).strip()

    except Exception as e:
        return f"Video summary failed: {str(e)[:100]}"

TOOL_FUNCTIONS = {
    "fetch_url": fetch_url, "calculator": calculator,
    "get_weather": get_weather, "run_python": run_python, "get_time": get_time,
    "video_summary": video_summary
}

@app.get("/", response_class=HTMLResponse)
async def home():
    with open(os.path.join(os.path.dirname(__file__), "ui.html"), encoding="utf-8") as f:
        return f.read()

@app.post("/agent")
async def agent_run(message: str = Form(...)):
    messages = [
        {"role": "system", "content": AGENT_PROMPT},
        {"role": "user", "content": message}
    ]
    steps = []

    for _ in range(6):  # Max 6 rounds
        resp = client.chat.completions.create(
            model="deepseek-chat", messages=messages, temperature=0.2
        )
        content = resp.choices[0].message.content.strip()

        # Extract JSON from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        content = content.strip()

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # Try to find JSON object in the response
            m = re.search(r'\{[^{}]*"action"[^{}]*\}', content)
            if m:
                try:
                    data = json.loads(m.group())
                except:
                    return {"answer": content, "reasoning": steps, "tool_calls": len(steps)}
            else:
                return {"answer": content, "reasoning": steps, "tool_calls": len(steps)}

        if data.get("action") == "answer":
            return {"answer": data.get("content", str(data)), "reasoning": steps, "tool_calls": len(steps)}

        if data.get("action") == "tool":
            tool = data.get("tool", "")
            args = data.get("args", {})
            if not isinstance(args, dict):
                args = {}
            fn = TOOL_FUNCTIONS.get(tool)
            if fn:
                try:
                    result = fn(**args) if args else fn()
                except Exception as e:
                    result = f"Tool error: {str(e)[:200]}"
            else:
                result = f"Unknown tool: {tool}"
            steps.append({"tool": tool, "args": str(args)[:200], "result": str(result)[:500]})
            messages.append({"role": "assistant", "content": content})
            messages.append({"role": "user", "content": f"Tool [{tool}] result:\n{result}\n\nDo you need more tools or can you answer now? Reply in JSON."})
            continue

        # Unknown action
        return {"answer": content, "reasoning": steps, "tool_calls": len(steps)}

    return {"answer": "Agent reached max rounds", "reasoning": steps, "tool_calls": len(steps)}

if __name__ == "__main__":
    import uvicorn; uvicorn.run(app, host="127.0.0.1", port=8863)
