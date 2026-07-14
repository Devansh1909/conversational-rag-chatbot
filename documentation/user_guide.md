# 🧑‍🏫 User Guide

This guide will help you get started with the RAG Chatbot and make the most of its features.

---

## 🚀 Getting Started

### 🛠️ First-Time Setup

1. **Install Python 3.9+** on your system
2. **Clone the repository** to your local machine
3. **Install dependencies** using:

   ```bash
   pip install -r requirements.txt
   ````

4. **Set up environment variables**:

   ```bash
   cp .env.example .env
   ```

Add your API keys to `.env`.

5. **Start the services** (FastAPI backend + Streamlit frontend)

---

### ▶️ Starting the Application

1. **Start the FastAPI backend** (Terminal 1):

   ```bash
   cd api
   uvicorn main:app --reload --port 8000
   ```

2. **Start the Streamlit frontend** (Terminal 2):

   ```bash
   cd app
   streamlit run streamlit_app.py
   ```

3. **Access the app**:

   * Streamlit UI: [http://localhost:8501](http://localhost:8501)
   * Swagger API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 💬 Using the Chatbot

### 📁 Uploading Documents

1. Open the Streamlit interface
2. Use the **sidebar** to upload documents
3. **Supported formats**:

   * `.pdf` (PDF)
   * `.docx` (Word)
   * `.html` (Web page)
4. **File size limit**: 200MB per file
5. Documents are automatically:

   * Split into chunks
   * Embedded into the FAISS vector index

---

### 🗨️ Chatting with Documents

1. Type your question into the input field
2. Press **Enter** or click **Send**
3. View the chatbot's response in the interface
4. Ask **follow-up questions** — the bot retains context

---

### 🧠 Conversational Memory

The bot supports **contextual memory**, so:

* Follow-up questions don’t need repeated context
* It remembers prior questions and answers
* You can refer to earlier discussion naturally

**Example:**

```
You: What is this document about?
Bot: This document discusses machine learning techniques...

You: Can you give more details on the algorithms?
Bot: Based on our discussion, the algorithms include...
```

---

### 🧩 Model Selection

From the sidebar, you can:

* Choose between models (e.g., GPT-4o-mini, GPT-4)
* Adjust response settings (if supported)
* View and manage uploaded documents

---

### 📂 Managing Documents

* View uploaded files in the sidebar
* Delete any file with a click
* Upload additional files anytime
* Monitor processing status of uploads

---

## ⚙️ Advanced Features

### 🔌 API Access

Interact programmatically using REST API.

```python
import requests

response = requests.post("http://localhost:8000/chat", json={
    "message": "What is this document about?",
    "session_id": "your_session_id"
})
print(response.json())
```

---

### 🧾 Session Management

* Each conversation is tied to a **unique session ID**
* Sessions persist in your browser session
* Refreshing the page will clear the memory

---

### 📈 LangSmith Integration (Optional)

If LangSmith is enabled:

* View live request traces
* Analyze latency and token usage
* Debug conversation flows

---

## 🛠️ Troubleshooting

### 🧨 Common Issues

**❗ "No documents uploaded"**

* Upload a document first
* Ensure it's `.pdf`, `.docx`, or `.html`

**🐢 Slow Responses**

* Large files take time to process
* Try breaking big files into smaller ones

**🔐 API Key Errors**

* Verify OpenAI key is set in `.env`
* Ensure sufficient credits and correct permissions

**❌ Connection Errors**

* Make sure both `FastAPI` and `Streamlit` are running
* Check that ports 8000 and 8501 are free
* Disable firewalls or proxies if needed

---

### 🔍 Getting Help

If something’s broken:

1. Check terminal logs for FastAPI and Streamlit
2. Open browser console (F12) to inspect errors
3. Recheck `.env` and config files
4. Reinstall dependencies with:

   ```bash
   pip install -r requirements.txt
   ```

---

## 💡 Tips for Best Results

### 📄 Document Preparation

* Use clear, well-structured content
* Avoid large images or tables
* Split huge docs into smaller logical files

### ❓ Question Asking

* Be specific (e.g., "Explain section 2")
* Use natural language
* Reference terms or names in the document
* Use follow-ups to dig deeper

### ⚡ Performance Optimization

* Upload in smaller batches
* Avoid huge single documents
* Refresh sessions when needed

---

Happy chatting! 🚀