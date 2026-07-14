
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic_models import QueryInput, QueryResponse, DocumentInfo, DeleteFileRequest
from langchain_utils import get_rag_chain
from db_utils import (
    insert_application_logs,
    get_chat_history,
    get_all_documents,
    insert_document_record,
    delete_document_record
)
from faiss_utils import index_document_to_faiss, delete_doc_from_faiss
import os
import uuid
import logging
import shutil
from datetime import datetime


logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="RAG Document QA System",
    description="Retrieval-Augmented Generation system using LangChain, "
                "HuggingFace embeddings, and FAISS for contextual document "
                "question answering.",
    version="1.0.0"
)


@app.post("/chat", response_model=QueryResponse)
def chat(query_input: QueryInput):
    """
    Process a user query against indexed documents using the RAG pipeline.
    
    Flow: Query → History-Aware Retriever → FAISS Search → LLM Generation → Response
    """
    session_id = query_input.session_id or str(uuid.uuid4())
    logger.info(
        f"Session ID: {session_id}, "
        f"User Query: {query_input.question}, "
        f"Model: {query_input.model.value}"
    )

    chat_history = get_chat_history(session_id)

    try:
        rag_chain = get_rag_chain(query_input.model.value)
        answer = rag_chain.invoke({
            "input": query_input.question,
            "chat_history": chat_history
        })['answer']
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    insert_application_logs(session_id, query_input.question, answer, query_input.model.value)
    logger.info(f"Session ID: {session_id}, AI Response: {answer}")

    return QueryResponse(
        answer=answer,
        session_id=session_id,
        model=query_input.model
    )


@app.post("/upload-doc")
def upload_and_index_document(file: UploadFile = File(...)):
    """
    Upload a document, process it through the ingestion pipeline, and index into FAISS.
    
    Pipeline: Upload → Save → Load → Chunk → Embed (HuggingFace) → FAISS Index
    """
    allowed_extensions = ['.pdf', '.docx', '.html', '.txt']
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
        )

    temp_file_path = f"temp_{file.filename}"

    try:
        # Save uploaded file to a temporary location
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_id = insert_document_record(file.filename)
        success = index_document_to_faiss(temp_file_path, file_id)

        if success:
            return {
                "message": f"File '{file.filename}' has been successfully uploaded and indexed.",
                "file_id": file_id
            }
        else:
            delete_document_record(file_id)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to index '{file.filename}'."
            )
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@app.get("/list-docs", response_model=list[DocumentInfo])
def list_documents():
    """Retrieve a list of all uploaded and indexed documents."""
    return get_all_documents()


@app.post("/delete-doc")
def delete_document(request: DeleteFileRequest):
    """
    Delete a document from both the FAISS vector store and the metadata database.
    """
    faiss_delete_success = delete_doc_from_faiss(request.file_id)

    if faiss_delete_success:
        db_delete_success = delete_document_record(request.file_id)
        if db_delete_success:
            return {
                "message": f"Successfully deleted document with file_id {request.file_id}."
            }
        else:
            return {
                "error": f"Deleted from FAISS but failed to delete from database (file_id={request.file_id})."
            }
    else:
        return {
            "error": f"Failed to delete document (file_id={request.file_id}) from FAISS."
        }


@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring the API status.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "vector_store": "FAISS",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
    }