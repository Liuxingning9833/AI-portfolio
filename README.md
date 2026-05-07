# AI Portfolio — 个人 AI 项目作品集

> 杭州 AI 岗位求职作品集，包含三个完整项目。

---

## 项目一：AI 聊天 API（FastAPI）

**技术栈**: FastAPI + DeepSeek API + Pydantic

**功能**:
- RESTful API 接口，支持多轮对话
- 会话管理（创建/查询/删除）
- 自动文档 Swagger UI
- 支持自定义 System Prompt

**启动**:
```bash
cd fastapi-chat
pip install -r requirements.txt
export DEEPSEEK_API_KEY=sk-your-key
uvicorn main:app --host 0.0.0.0 --port 8800
# 打开 http://127.0.0.1:8800/docs 查看接口文档
```

**API 端点**:
- `POST /chat` — 发送对话消息
- `GET /sessions` — 列出所有会话
- `GET /sessions/{id}` — 获取对话历史
- `DELETE /sessions/{id}` — 删除会话

---

## 项目二：本地知识库 RAG 问答（LangChain + ChromaDB）

**技术栈**: LangChain + ChromaDB + BGE 中文嵌入模型 + DeepSeek

**功能**:
- 支持上传 PDF/TXT/MD 文档
- 自动分块 + 向量化存储
- 语义检索 + LLM 精准回答
- 引用来源标注

**启动**:
```bash
cd rag-knowledge
pip install -r requirements.txt
export DEEPSEEK_API_KEY=sk-your-key
uvicorn main:app --host 127.0.0.1 --port 8851
```

---

## 项目三：AI 简历优化助手（DeepSeek 垂直场景）

**技术栈**: DeepSeek API + Streamlit

**功能**:
- 简历优化：STAR 法则重写，针对杭州 AI 岗位定制
- 岗位匹配：输入技能 → 推荐杭州在招岗位
- 模拟面试：AI 面试官出题 + 评分标准

**启动**:
```bash
cd resume-helper
pip install -r requirements.txt
export DEEPSEEK_API_KEY=sk-your-key
uvicorn main:app --host 127.0.0.1 --port 8851
```

---

## 整体技术能力

- **LLM 应用开发**: 熟悉 OpenAI 兼容 API，掌握多轮对话设计
- **RAG 系统**: 能用 LangChain + 向量数据库搭建知识库问答
- **API 开发**: 能用 FastAPI 构建 RESTful AI 服务
- **Prompt Engineering**: 针对不同场景设计 System Prompt，优化回答质量
- **前端**: 会用 Streamlit 快速搭建 AI 应用界面

## 环境变量

```bash
export DEEPSEEK_API_KEY=sk-your-deepseek-key
```

三个项目共享同一个 API Key。
