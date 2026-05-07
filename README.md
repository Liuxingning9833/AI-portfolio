# AI Portfolio — 个人 AI 项目作品集

> 作品集，包含五个完整项目。

---

## 启动方式（Windows）

打开命令行（Win+R → 输入 `cmd` → 回车），粘贴三行：

```
cd /d E:\AI\portfolio\项目文件夹名
set DEEPSEEK_API_KEY=sk-你的key
uvicorn main:app --host 127.0.0.1 --port 端口号
```

浏览器打开 `http://127.0.0.1:端口号`

---

## 项目一：AI 聊天 API

**技术栈**: FastAPI + DeepSeek

`http://127.0.0.1:8800`
`http://127.0.0.1:8800/docs`（接口文档）

---

## 项目二：知识库 RAG 问答

**技术栈**: FastAPI + DeepSeek + 关键词检索

`http://127.0.0.1:8861`

---

## 项目三：AI 简历优化助手

**技术栈**: FastAPI + DeepSeek + 流式输出

`http://127.0.0.1:8850`

---

## 项目四：AI 视频脚本批量生成器

**技术栈**: FastAPI + DeepSeek + CSV 批量处理

`http://127.0.0.1:8862`

---

## 项目五：AI Agent 智能体

**技术栈**: FastAPI + DeepSeek JSON Function Calling + 六工具

**功能**: AI 自主判断需求，调用工具完成任务
- 网页抓取、B站视频信息提取
- 数学计算、天气查询、Python 代码执行
- 时间查询

`http://127.0.0.1:8863`

---

## 技术能力

- **API 开发**: FastAPI 构建 RESTful AI 服务
- **LLM 应用**: OpenAI 兼容 API，多轮对话，流式输出
- **RAG 系统**: 文档检索增强生成，关键词匹配 + LLM 问答
- **Prompt Engineering**: System Prompt 设计，破限词，结构化输出
- **全栈开发**: 独立完成前后端，HTML/CSS/JS + Python
- **AI 视频**: LLM 批量生成分镜脚本和 AI 画面提示词
- **AI Agent**: Function Calling，自主调用工具完成任务

## 依赖安装

```cmd
pip install fastapi uvicorn python-multipart openai
```
