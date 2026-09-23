
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from api_utils import upload_document, list_documents, delete_document


def display_sidebar():
    """Render the sidebar with model selection, file upload, and document management."""

    # ── Model Selection ──
    st.sidebar.header("⚙️ Model Configuration")
    model_options = [
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-120b",
        "google/flan-t5-large",
        "mistralai/Mistral-7B-Instruct-v0.1",
        "gpt-4o-mini",
        "gpt-4o"
    ]
    model_labels = {
        "qwen/qwen3.8-27b": "⚡ Qwen 3.8-27B (Groq - Fast)",
        "openai/gpt-oss-120b": "⚡ GPT-OSS 120B (Groq - Fast)",
        "google/flan-t5-large": "🤗 Flan-T5-Large (HuggingFace)",
        "mistralai/Mistral-7B-Instruct-v0.1": "🤗 Mistral-7B-Instruct (HuggingFace)",
        "gpt-4o-mini": "🔑 GPT-4o-mini (OpenAI)",
        "gpt-4o": "🔑 GPT-4o (OpenAI)"
    }
    st.sidebar.selectbox(
        "Select LLM Model",
        options=model_options,
        format_func=lambda x: model_labels.get(x, x),
        key="model"
    )

    st.sidebar.divider()

    # ── Document Upload ──
    st.sidebar.header("📄 Document Upload")
    uploaded_file = st.sidebar.file_uploader(
        "Choose a file",
        type=["pdf", "docx", "html", "txt"]
    )
    if uploaded_file and st.sidebar.button("Upload & Index"):
        with st.spinner("Uploading and indexing document..."):
            upload_response = upload_document(uploaded_file)
            if upload_response:
                st.sidebar.success(
                    f"File uploaded successfully with ID {upload_response['file_id']}."
                )
                st.session_state.documents = list_documents()

    st.sidebar.divider()

    # ── Document Management ──
    st.sidebar.header("📂 Indexed Documents")
    if st.sidebar.button("🔄 Refresh Document List"):
        st.session_state.documents = list_documents()

    # Display document list and delete functionality
    if "documents" in st.session_state and st.session_state.documents:
        for doc in st.session_state.documents:
            st.sidebar.text(f"📎 {doc['filename']} (ID: {doc['id']})")

        selected_file_id = st.sidebar.selectbox(
            "Select a document to delete",
            options=[doc['id'] for doc in st.session_state.documents]
        )
        if st.sidebar.button("🗑️ Delete Selected Document"):
            delete_response = delete_document(selected_file_id)
            if delete_response:
                st.sidebar.success("Document deleted successfully.")
                st.session_state.documents = list_documents()