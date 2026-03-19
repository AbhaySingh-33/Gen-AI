import streamlit as st
from kg_agent import KGAgent

st.set_page_config(page_title="KG Chat Agent", page_icon="🤖", layout="wide")

st.title("🤖 Knowledge Graph Chat Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = KGAgent()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything about the knowledge graph..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.agent.chat(prompt)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
