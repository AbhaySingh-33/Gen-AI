import streamlit as st
from retrieval.retriever import retrieve
from retrieval.advanced_retriever import retrieve_advanced
from llm.models import llm
import time

st.set_page_config(page_title="LangChain RAG Assistant", page_icon="🦜", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Force light theme for main content */
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
    }
    
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin: 0;
    }
    .main-header p {
        color: #f0f0f0;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    .stChatMessage {
        background-color: #1e2130;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .source-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        color: white;
    }
    div[data-testid="stExpander"] {
        background-color: #1e2130;
        border-radius: 10px;
    }
    
    /* Fix ALL buttons - force white text */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5) !important;
    }
    .stButton > button p {
        color: white !important;
        font-size: 1rem !important;
    }
    
    /* Suggestion section styling */
    h3 {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🦜 LangChain RAG")
    st.markdown("---")
    
    retrieval_mode = st.radio(
        "🔧 Retrieval Mode",
        ["Standard", "Advanced (Query Decomposition)"],
        help="Advanced mode breaks complex queries into sub-queries"
    )
    
    st.markdown("---")
    st.markdown("#### 📊 Stats")
    
    if "messages" in st.session_state:
        st.metric("Questions Asked", len([m for m in st.session_state.messages if m["role"] == "user"]))
    
    st.markdown("---")
    st.markdown("#### ℹ️ About")
    st.info("This AI assistant uses advanced RAG techniques to answer questions about LangChain documentation.")
    
    st.markdown("#### 🎯 Features")
    st.markdown("""
    - 🔍 Multi-query retrieval
    - 🎯 Topic-based routing
    - 📚 Source citations
    - 💬 Chat history
    """)
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.markdown("""
<div class="main-header">
    <h1>🦜 LangChain RAG Assistant</h1>
    <p>Ask anything about LangChain - powered by advanced retrieval techniques</p>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "process_query" not in st.session_state:
    st.session_state.process_query = None

if not st.session_state.messages:
    st.markdown("### 💡 Try asking:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🤖 What are LangChain agents?", use_container_width=True, type="primary"):
            st.session_state.process_query = "What are LangChain agents?"
            st.rerun()
    
    with col2:
        if st.button("🔧 How do I use tools?", use_container_width=True, type="primary"):
            st.session_state.process_query = "How do I use tools in LangChain?"
            st.rerun()
    
    with col3:
        if st.button("📝 How to build a chatbot?", use_container_width=True, type="primary"):
            st.session_state.process_query = "How do I build a chatbot with LangChain?"
            st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("📚 View Sources"):
                for i, source in enumerate(message["sources"], 1):
                    st.markdown(f"<div class='source-card'><b>📄 Source {i}</b><br>{source[:250]}...</div>", unsafe_allow_html=True)

# Process button click query
if st.session_state.process_query:
    prompt = st.session_state.process_query
    st.session_state.process_query = None
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🔍 Searching knowledge base..."):
            time.sleep(0.5)
            if retrieval_mode == "Advanced (Query Decomposition)":
                docs = retrieve_advanced(prompt)
            else:
                docs = retrieve(prompt)
            
        with st.spinner("🧠 Generating answer..."):
            context = "\n".join([d.page_content for d in docs])
            
            llm_prompt = f"""Use the context to answer the question.

Context:
{context}

Question:
{prompt}
"""
            response = llm.invoke(llm_prompt)
            answer = response.content
            
            st.markdown(answer)
            
            sources = [doc.page_content for doc in docs]
            
            with st.expander("📚 View Sources"):
                for i, doc in enumerate(docs, 1):
                    st.markdown(f"<div class='source-card'><b>📄 Source {i}</b><br>{doc.page_content[:250]}...</div>", unsafe_allow_html=True)
    
    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
    st.rerun()

if prompt := st.chat_input("💬 Ask a question about LangChain..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🔍 Searching knowledge base..."):
            time.sleep(0.5)
            if retrieval_mode == "Advanced (Query Decomposition)":
                docs = retrieve_advanced(prompt)
            else:
                docs = retrieve(prompt)
            
        with st.spinner("🧠 Generating answer..."):
            context = "\n".join([d.page_content for d in docs])
            
            llm_prompt = f"""Use the context to answer the question.

Context:
{context}

Question:
{prompt}
"""
            response = llm.invoke(llm_prompt)
            answer = response.content
            
            st.markdown(answer)
            
            sources = [doc.page_content for doc in docs]
            
            with st.expander("📚 View Sources"):
                for i, doc in enumerate(docs, 1):
                    st.markdown(f"<div class='source-card'><b>📄 Source {i}</b><br>{doc.page_content[:250]}...</div>", unsafe_allow_html=True)
    
    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
