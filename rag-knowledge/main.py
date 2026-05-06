"""本地知识库 RAG 问答系统 — LangChain + ChromaDB + DeepSeek
支持 PDF/TXT/MD 文档导入，向量检索 + LLM 回答
启动: streamlit run main.py
"""
import os, tempfile
import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

st.set_page_config(page_title="知识库问答", page_icon="📚")
st.title("📚 本地知识库 RAG 问答系统")

# 初始化
PERSIST_DIR = "./chroma_db"
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

@st.cache_resource
def get_embeddings():
    return HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")

@st.cache_resource
def get_llm():
    return ChatOpenAI(
        model="deepseek-chat",
        api_key=API_KEY,
        base_url="https://api.deepseek.com",
        temperature=0.3
    )

# 侧边栏: 文档上传
with st.sidebar:
    st.header("📁 上传文档")
    uploaded = st.file_uploader("支持 PDF / TXT / MD", type=["pdf","txt","md"], accept_multiple_files=True)

    if uploaded and st.button("🔨 构建知识库"):
        with st.spinner("处理文档中..."):
            docs = []
            for f in uploaded:
                suffix = f.name.split(".")[-1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp:
                    tmp.write(f.read())
                    tmp_path = tmp.name

                if suffix == "pdf":
                    loader = PyPDFLoader(tmp_path)
                else:
                    loader = TextLoader(tmp_path, encoding="utf-8")

                loaded = loader.load()
                for d in loaded:
                    d.metadata["source"] = f.name
                docs.extend(loaded)
                os.unlink(tmp_path)

            # 分块
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
            chunks = splitter.split_documents(docs)

            # 向量化存储
            embeddings = get_embeddings()
            vectordb = Chroma.from_documents(chunks, embeddings, persist_directory=PERSIST_DIR)
            st.session_state["vectordb"] = vectordb
            st.success(f"✅ 已处理 {len(docs)} 个文档 → {len(chunks)} 个文本块")

    if st.button("🗑 清空知识库"):
        import shutil
        if os.path.exists(PERSIST_DIR):
            shutil.rmtree(PERSIST_DIR)
        st.session_state.pop("vectordb", None)
        st.success("已清空")

# 主区域: 问答
query = st.text_input("🔍 输入你的问题", placeholder="例如: 这篇文章的核心观点是什么？")

if query:
    vectordb = st.session_state.get("vectordb")
    if not vectordb:
        try:
            embeddings = get_embeddings()
            vectordb = Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)
            st.session_state["vectordb"] = vectordb
        except:
            st.warning("⚠️ 请先上传文档构建知识库")
            st.stop()

    with st.spinner("检索中..."):
        # 检索相关文档
        retriever = vectordb.as_retriever(search_kwargs={"k": 3})
        rel_docs = retriever.invoke(query)

        # 构建 prompt
        context = "\n\n".join([f"[来源: {d.metadata.get('source','未知')}]\n{d.page_content}" for d in rel_docs])

        prompt = PromptTemplate(
            template="""你是一个知识库助手。请根据以下参考资料回答问题。
如果参考资料中没有相关信息，就说"根据现有资料，无法回答此问题"。

【参考资料】
{context}

【用户问题】
{question}

【回答】""",
            input_variables=["context", "question"]
        )

        # 调用 LLM
        llm = get_llm()
        chain = prompt | llm

        response = chain.invoke({"context": context, "question": query})
        answer = response.content if hasattr(response, 'content') else str(response)

        # 显示结果
        st.markdown("### 📝 回答")
        st.write(answer)

        # 显示来源
        with st.expander("📖 参考来源"):
            for i, doc in enumerate(rel_docs):
                source = doc.metadata.get("source", "未知")
                st.caption(f"**来源 {i+1}:** {source}")
                st.text(doc.page_content[:300] + "...")
                st.divider()

st.caption("💡 提示：在侧边栏上传 PDF/TXT 文档，系统自动分词 → 向量化 → 可检索问答")
st.caption(f"🔑 API Key: {'已设置' if API_KEY else '❌ 未设置 (export DEEPSEEK_API_KEY=sk-...)'}")
