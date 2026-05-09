<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/DeepSeek-V4-536DFE?logo=openai" alt="DeepSeek">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

<h1 align="center">AI Portfolio</h1>
<p align="center">五个完整的 AI 应用项目，基于 DeepSeek 大模型</p>

---

## 项目总览

| # | 项目 | 技术栈 | 演示地址 |
|---|------|--------|---------|
| 1 | AI 聊天 API | FastAPI + DeepSeek | `:8800` |
| 2 | 知识库 RAG | FastAPI + 向量检索 + DeepSeek | `:8861` |
| 3 | AI 简历助手 | FastAPI + DeepSeek + 流式输出 | `:8850` |
| 4 | AI 视频脚本生成器 | FastAPI + DeepSeek + CSV 批量 | `:8862` |
| 5 | AI Agent 智能体 | FastAPI + JSON Agent Loop + 6 工具 | `:8863` |

---

## 1. AI 聊天 API

> RESTful AI 对话服务，支持多轮会话、Swagger 自动文档

| 功能 | 说明 |
|------|------|
| POST /chat | 发送消息，自动管理会话 |
| GET /sessions | 列出所有对话 |
| 网页聊天界面 | 根路径直接聊 |

```
http://127.0.0.1:8800     聊天界面
http://127.0.0.1:8800/docs 接口文档
```

---

## 2. 知识库 RAG 问答

> 上传文档 → 自动检索 → AI 精准回答

| 功能 | 说明 |
|------|------|
| 文档上传 | 支持 PDF / TXT / MD |
| 智能检索 | 关键词匹配 + 上下文提取 |
| 来源标注 | 每句回答标注出处 |

```
http://127.0.0.1:8861
```

---

## 3. AI 简历优化助手

> 针对杭州 AI 岗位的求职辅助工具

| 功能 | 说明 |
|------|------|
| 简历优化 | STAR 法则重写 + 关键词补全 |
| 岗位匹配 | 输入技能 → 推荐岗位 + 公司 |
| 模拟面试 | AI 出题 + 评分标准 |

```
http://127.0.0.1:8850
```

---

## 4. AI 视频脚本批量生成器

> 输入产品 → 出完整分镜脚本 + AI 画面提示词

| 功能 | 说明 |
|------|------|
| 单条生成 | 填写产品名+描述 → 出脚本 |
| 批量处理 | 上传 CSV → 批量生成全部产品 |
| 结果导出 | 一键导出全部脚本 |

```
http://127.0.0.1:8862
```

---

## 5. AI Agent 智能体

> AI 自主判断需求，调用工具完成任务

| 工具 | 能力 |
|------|------|
| fetch_url | 抓取任意网页内容 |
| video_summary | B 站视频信息提取 |
| calculator | 数学表达式计算 |
| get_weather | 全球城市天气查询 |
| run_python | 安全执行 Python 代码 |
| get_time | 当前时间查询 |

```
http://127.0.0.1:8863
```

---

## 快速启动

```bash
# 1. 设置 API Key
set DEEPSEEK_API_KEY=sk-your-key

# 2. 安装依赖
pip install fastapi uvicorn python-multipart openai

# 3. 启动任意项目
cd 项目文件夹
uvicorn main:app --host 127.0.0.1 --port 端口号
```

---

## 技术能力覆盖

- **LLM 应用开发**: OpenAI 兼容 API，多轮对话，流式输出
- **RAG 系统**: 文档检索增强生成
- **AI Agent**: JSON Function Calling，自主工具调用
- **API 开发**: FastAPI RESTful 服务，Swagger 文档
- **Prompt Engineering**: 结构化 System Prompt，多场景适配
- **全栈开发**: Python 后端 + HTML/CSS/JS 前端
- **Web 抓取**: 静态页面解析 + 公开 API 调用
