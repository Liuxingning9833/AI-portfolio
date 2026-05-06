"""AI 简历优化助手 — DeepSeek API 垂直场景应用
功能: 简历优化 / 岗位匹配 / 模拟面试
启动: streamlit run main.py
"""
import os, json
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="AI 简历助手", page_icon="🎯")
st.title("🎯 AI 简历优化助手 — 杭州 AI 岗位专属")

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

SYSTEM = """你是杭州AI行业的资深HR兼职业顾问。你了解杭州AI产业生态
（DeepSeek、阿里巴巴、字节跳动AI部门、AI创业公司等）。
你擅长: 简历优化、岗位匹配、模拟面试。
回答用简洁实用的语言，不说废话，直接给可操作的建议。"""

def ask_ai(prompt, temperature=0.7):
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role":"system","content":SYSTEM}, {"role":"user","content":prompt}],
        temperature=temperature
    )
    return resp.choices[0].message.content

# 三个 Tab
tab1, tab2, tab3 = st.tabs(["📝 简历优化", "🎯 岗位匹配", "💬 模拟面试"])

# === Tab 1: 简历优化 ===
with tab1:
    st.subheader("粘贴你的简历，AI 帮你优化")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("姓名")
        target_job = st.selectbox("目标岗位", [
            "AI应用工程师", "AIGC提示词工程师", "AI视频生成师",
            "AI产品助理", "AI客户成功", "AI数据分析师", "其他"
        ])
    with col2:
        exp_years = st.selectbox("工作经验", ["应届/零经验", "1-2年", "3-5年", "5年以上"])
        education = st.selectbox("学历", ["本科", "大专", "硕士", "博士"])

    original = st.text_area("原始简历内容", height=200,
        placeholder="粘贴你的简历文字...\n\n例如:\n2020年毕业于大连外国语大学软件工程\n熟悉Python基础，了解AI工具使用\n有小红书账号运营经验...")

    if st.button("✨ 优化简历", type="primary"):
        if not original:
            st.warning("请先粘贴简历")
        else:
            prompt = f"""请优化以下简历，使其更适合投递杭州的「{target_job}」岗位。

求职者背景: {name}，{education}，{exp_years}

优化要求:
1. 用 STAR 法则重写经历（情境-任务-行动-结果）
2. 补充与 {target_job} 相关的技能关键词
3. 量化成果（没有数据就合理估算）
4. 控制在 500 字以内
5. 去掉与目标岗位无关的内容
6. 添加「技能」「项目经历」「证书」三个板块

原始简历:
{original}

请输出优化后的完整简历:"""
            with st.spinner("优化中..."):
                result = ask_ai(prompt)
                st.markdown("### 优化后简历")
                st.markdown(result)
                st.download_button("📥 下载优化简历", result, f"{name}_简历.md")

# === Tab 2: 岗位匹配 ===
with tab2:
    st.subheader("输入你的技能，匹配杭州在招岗位")

    skills = st.text_area("你的技能（一行一个）", height=120,
        placeholder="Python\nPrompt Engineering\n剪映\n小红书运营\nAI工具使用(DeepSeek/Claude)\n基础前端(HTML/CSS)")

    target_city = st.selectbox("目标城市", ["杭州", "杭州(可远程)", "不限"])

    if st.button("🔍 匹配岗位", type="primary"):
        if not skills:
            st.warning("请输入技能")
        else:
            prompt = f"""求职者技能:
{skills}

目标城市: {target_city}

请完成以下分析:
1. 推荐 3-5 个最适合的杭州在招岗位（具体到岗位名称）
2. 每个岗位说明: 薪资范围、核心要求、匹配度(百分比)
3. 哪些技能需要补强？给出优先级排序
4. 推荐 3 家杭州值得投递的公司
5. 下一步行动建议"""
            with st.spinner("分析中..."):
                result = ask_ai(prompt)
                st.markdown(result)

# === Tab 3: 模拟面试 ===
with tab3:
    st.subheader("AI 模拟面试官")

    job = st.selectbox("面试岗位", [
        "AI应用工程师", "AIGC提示词工程师", "AI视频生成师",
        "AI产品助理", "AI客户成功"
    ])
    level = st.select_slider("难度", ["初级", "中级", "高级"], value="初级")

    if st.button("🎤 生成面试题", type="primary"):
        prompt = f"""你是杭州一家AI公司的面试官，正在招聘「{job}」（{level}）。

请生成 5 道面试题:
1. 每道题标注考察点
2. 题后附上评分标准
3. 最后给一个范例回答

题目应该考察实际动手能力，而非背诵知识点。"""
        with st.spinner("出题中..."):
            result = ask_ai(prompt, temperature=0.9)
            st.markdown(result)

    # 自由问答
    st.divider()
    st.caption("💬 也可以直接向面试官提问:")
    q = st.text_input("你的问题", placeholder="例如: 我没有相关工作经验，面试怎么回答？", key="interview_q")
    if q:
        with st.spinner("..."):
            st.markdown(ask_ai(f"求职者问: {q}\n请以杭州AI行业面试官的身份回答。"))

st.sidebar.caption(f"🔑 API Key: {'已设置 ✅' if API_KEY else '❌ 未设置'}")
st.sidebar.caption("💡 设置: export DEEPSEEK_API_KEY=sk-...")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📁 项目信息")
st.sidebar.markdown("- 技术栈: DeepSeek API + Streamlit")
st.sidebar.markdown("- 场景: 杭州 AI 求职辅助")
st.sidebar.markdown("- GitHub: [你的仓库链接]")
