<p align="center">
  <img src="https://img.shields.io/badge/OS-Windows%2011-blue?logo=windows" alt="OS">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/DeepSeek-V4-536DFE?logo=openai" alt="DeepSeek">
  <img src="https://img.shields.io/badge/Build-Success-brightgreen" alt="Build">
</p>

<h1 align="center">AI Portfolio</h1>
<p align="center"><strong>个人 AI 应用作品集 · 五个完整项目</strong></p>

---

## 项目描述

AI Portfolio 是一个涵盖 LLM 应用开发全链路的个人项目集合。基于 DeepSeek 大模型，从基础 API 对话到智能体自主决策，展示了 AI 应用从接口设计、知识检索、场景落地到 Agent 开发的完整能力。

五个项目覆盖：RESTful API 设计、RAG 知识库、流式输出、批量任务处理、JSON Function Calling 智能体。

---

## 项目结构

- **`fastapi-chat/`** — AI 聊天 API，支持多轮对话、会话管理、Swagger 文档
  - `main.py` — FastAPI 服务入口，含聊天网页界面
  - `requirements.txt` — Python 依赖

- **`rag-knowledge/`** — 知识库 RAG 问答，文档上传、检索、LLM 回答
  - `main.py` — FastAPI 服务入口
  - `ui.html` — 前端交互界面
  - `requirements.txt` — Python 依赖
  - `杭州AI行业资料.txt` — 测试用文档

- **`resume-helper/`** — AI 简历助手，支持简历优化、岗位匹配、模拟面试
  - `main.py` — FastAPI 服务入口，含流式输出
  - `ui.html` — 前端交互界面
  - `requirements.txt` — Python 依赖

- **`video-generator/`** — AI 视频脚本批量生成器，输入产品信息自动出分镜脚本
  - `main.py` — FastAPI 服务入口
  - `ui.html` — 前端交互界面
  - `requirements.txt` — Python 依赖

- **`ai-agent/`** — AI Agent 智能体，六工具自主调用
  - `main.py` — FastAPI 服务入口，JSON Function Calling Agent 循环
  - `ui.html` — 前端交互界面，可视化思维过程
  - `requirements.txt` — Python 依赖

- **`学习计划.md`** — Python + ACP 备考 + 求职计划
- **`screenshots/`** — 项目运行截图

---

## 功能特性

### 1. AI 聊天 API

提供 RESTful AI 对话接口，支持多轮会话管理和 Swagger 自动文档。内置网页聊天界面，开箱即用。

- `POST /chat` — 发送消息，自动管理会话
- `GET /sessions` — 列出所有对话
- `GET /sessions/{id}` — 获取对话历史
- `DELETE /sessions/{id}` — 删除会话

### 2. 知识库 RAG 问答

上传 PDF/TXT/Markdown 文档，系统自动分词、检索、调用大模型精准回答，并标注引用来源。

- 支持多文档批量上传
- 关键词匹配 + 上下文提取
- 回答标注来源出处

### 3. AI 简历优化助手

针对杭州 AI 岗位设计的智能求职辅助工具，包含三个模块：

- **简历优化** — STAR 法则重写，关键词补全，针对目标岗位定制
- **岗位匹配** — 输入技能，推荐杭州在招岗位与公司
- **模拟面试** — AI 出题，标注考察点与评分标准

### 4. AI 视频脚本批量生成器

输入产品信息，AI 自动生成完整短视频分镜脚本，包含时间轴、画面描述、字幕旁白、音效、AI 画面提示词和拍摄建议。

- **单条生成** — 填写产品名和描述，一键生成
- **批量处理** — 上传 CSV，批量处理全部产品
- **结果导出** — 一键导出全部脚本

### 5. AI Agent 智能体

AI 自主判断用户需求，调用合适工具完成任务。采用 JSON Function Calling 架构，可视化展示思考和工具调用过程。

| 工具 | 能力 |
|------|------|
| `fetch_url` | 抓取任意网页内容并提取正文 |
| `video_summary` | 通过 Bilibili API 提取视频信息（标题/播放量/UP主） |
| `calculator` | 数学表达式计算（支持三角函数/对数） |
| `get_weather` | 全球城市天气查询 |
| `run_python` | 安全沙箱执行 Python 代码 |
| `get_time` | 当前时间查询 |

---

## 环境要求

- **Python 3.10 及以上版本**
- **操作系统：** Windows 10/11

### 所需 Python 库

| 库 | 用途 |
|---|---|
| `fastapi` | Web API 框架 |
| `uvicorn` | ASGI 服务器 |
| `openai` | DeepSeek API 调用 |
| `python-multipart` | 表单文件上传 |

**安装：**
```bash
pip install fastapi uvicorn openai python-multipart
```

---

## 运行 DEMO

### 1. 克隆项目

```bash
git clone https://github.com/Liuxingning9833/AI-portfolio
cd AI-portfolio
```

### 2. 安装依赖

```bash
pip install fastapi uvicorn openai python-multipart
```

### 3. 配置 API Key

在命令行中设置环境变量：

```bash
set DEEPSEEK_API_KEY=你的DeepSeek-API-Key
```

### 4. 启动项目

启动你想运行的项目（每个项目对应一个端口）：

```bash
# AI 聊天 API
cd fastapi-chat
uvicorn main:app --host 127.0.0.1 --port 8800

# AI 简历助手
cd resume-helper
uvicorn main:app --host 127.0.0.1 --port 8850

# 知识库 RAG
cd rag-knowledge
uvicorn main:app --host 127.0.0.1 --port 8861

# 视频脚本生成
cd video-generator
uvicorn main:app --host 127.0.0.1 --port 8862

# AI Agent 智能体
cd ai-agent
uvicorn main:app --host 127.0.0.1 --port 8863
```

### 5. 访问系统

在浏览器中输入对应端口号即可使用：

| 项目 | 访问地址 |
|------|---------|
| AI 聊天 API | `http://127.0.0.1:8800` |
| API 接口文档 | `http://127.0.0.1:8800/docs` |
| AI 简历助手 | `http://127.0.0.1:8850` |
| 知识库 RAG | `http://127.0.0.1:8861` |
| 视频脚本生成 | `http://127.0.0.1:8862` |
| AI Agent | `http://127.0.0.1:8863` |

### 6. 操作流程

1. **启动服务** — 在命令行运行 `uvicorn main:app --host 127.0.0.1 --port 端口号`
2. **打开浏览器** — 访问对应端口
3. **测试 AI 聊天** — 输入消息，体验多轮对话
4. **测试简历优化** — 粘贴简历，切换标签体验岗位匹配和模拟面试
5. **测试知识库** — 上传文档，构建知识库后提问
6. **测试视频脚本** — 填写产品信息，生成完整分镜脚本
7. **测试 AI Agent** — 输入复杂问题，观察 Agent 思考和工具调用过程

---

## 技术栈

| 类别 | 技术 |
|---|---|
| **编程语言** | Python 3.12 |
| **AI 模型** | DeepSeek API（对话、检索、Agent 决策） |
| **Web 框架** | FastAPI |
| **API 风格** | RESTful + OpenAI 兼容接口 |
| **前端** | 原生 HTML/CSS/JS（内嵌式 SPA） |
| **Agent 架构** | JSON Function Calling + Agent Loop |
| **RAG 方案** | 关键词匹配检索 + LLM 生成 |
| **数据存储** | 本地 JSON 文件 / ChromaDB |
| **流式输出** | Server-Sent Events |

---

> **项目地址：** [GitHub - Liuxingning9833/AI-portfolio](https://github.com/Liuxingning9833/AI-portfolio)
