# System Information: Conversational RAG Chatbot

## 1. What is this Project?

This project is a **Conversational Document Question & Answering (Q&A) System** built using **Retrieval-Augmented Generation (RAG)**.

In simple terms:
- You upload documents (like **PDFs**, **Word documents**, **Text files**, or **HTML pages**).
- The system reads, analyzes, and remembers the content of those documents.
- You can chat with an AI assistant about the contents of your uploaded documents.
- The assistant answers **only based on your documents** and will not make things up (anti-hallucination).
- The assistant remembers earlier questions and answers in your chat session so you can ask natural follow-up questions (e.g., *"What did you mean by that?"* or *"Can you summarize the second point?"*).

---

## 2. High-Level Architecture Overview

The system is split into two independent parts:

```
[ User Browser ]
       │
       ▼
┌───────────────────────────────┐
│     Streamlit Frontend        │  <-- Interactive Chat UI & File Uploads
│     (Runs on Port 8501)       │
└──────────────┬────────────────┘
               │  HTTP REST Requests
               ▼
┌───────────────────────────────┐
│      FastAPI Backend          │  <-- REST API & Orchestration
│     (Runs on Port 8001)       │
├──────────────┬────────────────┤
│   LangChain  │   Embeddings   │  <-- Document chunking & AI Prompting
├──────────────┼────────────────┤
│  FAISS Index │ SQLite DB      │  <-- Vector Store & Chat History/Metadata
└──────────────┴────────────────┘
```

1. **Frontend (Streamlit)**: A clean web interface where users can select models, upload documents, manage existing files, and chat.
2. **Backend (FastAPI)**: An API server that handles file ingestion, text chunking, vector embeddings, similarity search, database logging, and calling the LLM.

---

## 3. Core Technologies Used

| Technology | Role | Why it is used |
| :--- | :--- | :--- |
| **Streamlit** | Frontend Web UI | Quick, interactive UI for chatting and uploading files without complex frontend setup. |
| **FastAPI** | Backend Web Framework | High-performance, lightweight Python REST API framework. |
| **LangChain** | RAG Pipeline Orchestrator | Connects prompt templates, chat history, document retrieval, and LLM calls. |
| **FAISS (Facebook AI Similarity Search)** | Vector Database | Stores document chunks as vector embeddings on disk and performs fast similarity searches. |
| **HuggingFace Embeddings** (`all-MiniLM-L6-v2`) | Text Vectorizer | Converts text chunks into mathematical vectors (384 dimensions) on the local CPU without external API costs. |
| **SQLite** (`rag_app.db`) | Relational Database | Stores document upload records and conversation history per session. |
| **LLMs (Groq, HuggingFace, OpenAI)** | Large Language Models | Generates natural language answers based strictly on retrieved document context. |

---

## 4. How the System Works (Step-by-Step)

### A. Document Upload & Ingestion Flow
When a user uploads a document:
1. **Upload**: User selects a file (`.pdf`, `.docx`, `.html`, or `.txt`) in the Streamlit sidebar.
2. **Transfer**: The frontend sends the file as a `multipart/form-data` POST request to `/upload-doc` on the FastAPI server.
3. **Database Record**: The backend inserts a record for the document in SQLite (`document_store` table) and receives a unique `file_id`.
4. **Document Loading**: The system chooses the right loader:
   - `PyPDFLoader` for `.pdf`
   - `Docx2txtLoader` for `.docx`
   - `UnstructuredHTMLLoader` for `.html`
   - `TextLoader` for `.txt`
5. **Text Chunking**: The text is broken into small, manageable pieces:
   - Chunk size: **500 characters**
   - Chunk overlap: **50 characters** (prevents context cutoff between pieces)
6. **Vector Embedding**: Each chunk is transformed into vector numbers using the local `sentence-transformers/all-MiniLM-L6-v2` model.
7. **Storage**: Each chunk is tagged with its `file_id` and saved into the local FAISS index (`./faiss_index` directory).

---

### B. Chat & Question Answering Flow (RAG Pipeline)
When a user asks a question in the chat interface:
1. **Send Query**: Streamlit sends the user question, `session_id`, and selected model to `/chat`.
2. **Fetch History**: The API looks up previous exchanges from SQLite (`application_logs`) for that `session_id`.
3. **Contextualize Question**:
   - If the user asks a follow-up like *"Tell me more about the first item"*, the **History-Aware Retriever** uses the LLM to rewrite it into a self-contained question: *"What are the details of the first item mentioned earlier?"*
4. **FAISS Similarity Search**:
   - The standalone question is converted into an embedding.
   - FAISS searches the vector store and finds the **top 3 most relevant text chunks** (`k=3`).
5. **Prompt Construction (Anti-Hallucination)**:
   - The system inserts the 3 retrieved chunks into a strict system prompt:
     > *"Answer the user's question relying ONLY and EXCLUSIVELY on the provided Context below. If the answer is NOT explicitly stated in or directly supported by the provided Context, you MUST answer with: 'I don't know, there is no such thing given in these documents.' Do not guess or assume."*
6. **LLM Generation**: The selected LLM (Groq, HuggingFace, or OpenAI) generates a concise, accurate response based solely on the context.
7. **Log & Return**:
   - The query and answer are saved to SQLite for history tracking.
   - The answer and `session_id` are sent back to Streamlit and displayed to the user.

---

### C. Document Deletion Flow
When a user deletes a document:
1. The user selects a document in the sidebar and clicks **Delete**.
2. Streamlit calls `POST /delete-doc` with the `file_id`.
3. The backend iterates over the FAISS vector store, filters out chunks matching that `file_id`, and saves the updated index. If no documents remain, the FAISS index folder is cleaned up.
4. The record in the SQLite `document_store` table is removed.

---

## 5. File Structure and What Each File Does

```text
Conversational_RAG/
├── api/                          # Backend Services
│   ├── main.py                   # FastAPI app with endpoints (/chat, /upload-doc, /list-docs, /delete-doc, /health)
│   ├── langchain_utils.py        # LangChain logic: history-aware retriever, prompt templates, LLM switch
│   ├── faiss_utils.py            # File loading, text chunking, HuggingFace embeddings, FAISS indexing/deletion
│   ├── db_utils.py               # SQLite helpers for chat history and document metadata
│   ├── pydantic_models.py        # Data models and request/response validation schemas
│   ├── rag_app.db                # Local SQLite database file
│   └── faiss_index/              # Local directory containing serialized FAISS index files
│
├── app/                          # Frontend User Interface
│   ├── streamlit_app.py          # Main Streamlit UI entry point
│   ├── sidebar.py                # Sidebar UI: Model selector, file uploader, document manager
│   ├── chat_interface.py         # Main chat window with message history and expandable answer details
│   └── api_utils.py              # Helper functions to call the FastAPI endpoints from Streamlit
│
├── docs/                         # Sample PDF documents for testing
│   ├── RAG_Document_1.pdf
│   ├── RAG_Document_2.pdf
│   ├── RAG_Document_3.pdf
│   ├── RAG_Document_4.pdf
│   └── RAG_Document_5.pdf
│
├── documentation/                # Developer & User guides
│   ├── api_reference.md          # Technical documentation for API endpoints
│   └── user_guide.md             # How-to guide for end users
│
├── .env                          # Local environment variables (API keys)
├── .env.example                  # Template showing needed environment keys
├── requirements.txt              # Python package dependencies
└── README.md                     # High-level overview and instructions
```

---

## 6. Supported AI Models

The system is configured with a model switch in `api/langchain_utils.py` and `app/sidebar.py`:

| Provider | Model Identifier | Description |
| :--- | :--- | :--- |
| **Groq (Fastest)** | `qwen/qwen3.8-27b` | Ultra-fast inference with Qwen model via Groq API. |
| **Groq (Fastest)** | `openai/gpt-oss-120b` | Open-weight high parameter model on Groq. |
| **HuggingFace** | `google/flan-t5-large` | Open-source sequence-to-sequence model hosted on Hugging Face Hub. |
| **HuggingFace** | `mistralai/Mistral-7B-Instruct-v0.1` | Instruction-tuned open model hosted on Hugging Face Hub. |
| **OpenAI** | `gpt-4o-mini` | Cost-effective, high quality OpenAI model. |
| **OpenAI** | `gpt-4o` | Flagship OpenAI model. |

---

## 7. Database Tables (SQLite)

The SQLite database `rag_app.db` maintains two tables:

### 1. `application_logs`
Tracks all questions, answers, and models per conversation session:
- `id` (INTEGER, Primary Key)
- `session_id` (TEXT)
- `user_query` (TEXT)
- `gpt_response` (TEXT)
- `model` (TEXT)
- `created_at` (TIMESTAMP)

### 2. `document_store`
Tracks uploaded files and their IDs:
- `id` (INTEGER, Primary Key)
- `filename` (TEXT)
- `upload_timestamp` (TIMESTAMP)

---

## 8. Summary of API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/chat` | Processes a chat prompt, retrieves relevant chunks, and returns an answer. |
| `POST` | `/upload-doc` | Uploads a file, extracts text, chunks it, embeds it, and stores in FAISS. |
| `GET` | `/list-docs` | Returns a list of all currently indexed documents. |
| `POST` | `/delete-doc` | Deletes a document from both FAISS and the SQLite database. |
| `GET` | `/health` | Returns server health, active embedding model, and vector store type. |

---

## 9. How to Run the Project

1. **Activate Virtual Environment & Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**:
   In your `.env` file, supply at least one API key:
   ```ini
   GROQ_API_KEY=your_groq_key_here
   # OR
   HUGGINGFACEHUB_API_TOKEN=your_hf_token_here
   # OR
   OPENAI_API_KEY=your_openai_key_here
   ```

3. **Start the FastAPI Backend**:
   ```bash
   cd api
   uvicorn main:app --reload --port 8001
   ```

4. **Start the Streamlit Frontend**:
   ```bash
   cd app
   streamlit run streamlit_app.py
   ```
