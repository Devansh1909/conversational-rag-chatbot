
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from sidebar import display_sidebar
from chat_interface import display_chat_interface

# ── Page Configuration ──
st.set_page_config(
    page_title="RAG Document QA System",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 RAG Document QA System")
st.caption("Powered by LangChain · FAISS · HuggingFace Embeddings")

# ── Initialize Session State ──
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = None

# ── Render UI ──
display_sidebar()
display_chat_interface()