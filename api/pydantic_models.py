
from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class ModelName(str, Enum):
    """
    Supported LLM models for the RAG pipeline.
    
    Groq Models (Ultra-fast):
        - GROQ_QWEN: Qwen 3.8-27B
        - GROQ_GPT_OSS: OpenAI GPT-OSS-120B
    
    HuggingFace Models:
        - FLAN_T5: Google's Flan-T5-Large
        - MISTRAL: Mistral-7B-Instruct
    
    OpenAI Models:
        - GPT4_O_MINI: GPT-4o-mini
        - GPT4_O: GPT-4o
    """
    GROQ_QWEN = "qwen/qwen3.8-27b"
    GROQ_GPT_OSS = "openai/gpt-oss-120b"
    FLAN_T5 = "google/flan-t5-large"
    MISTRAL = "mistralai/Mistral-7B-Instruct-v0.1"
    GPT4_O_MINI = "gpt-4o-mini"
    GPT4_O = "gpt-4o"


class QueryInput(BaseModel):
    """Schema for incoming chat queries."""
    question: str
    session_id: str = Field(default=None)
    model: ModelName = Field(default=ModelName.GROQ_QWEN)


class QueryResponse(BaseModel):
    """Schema for chat responses."""
    answer: str
    session_id: str
    model: ModelName


class DocumentInfo(BaseModel):
    """Schema for document metadata returned by list-docs endpoint."""
    id: int
    filename: str
    upload_timestamp: datetime


class DeleteFileRequest(BaseModel):
    """Schema for document deletion requests."""
    file_id: int