
from dotenv import load_dotenv
load_dotenv()

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document
try:
    from langchain.chains import create_history_aware_retriever, create_retrieval_chain
    from langchain.chains.combine_documents import create_stuff_documents_chain
except ImportError:
    from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
    from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from typing import List
import os
import logging

from faiss_utils import get_retriever

logger = logging.getLogger(__name__)

output_parser = StrOutputParser()


# Contextualization prompt: Reformulates follow-up questions into standalone queries
# This enables the retriever to find relevant documents even when the user's question
# references prior conversation context (e.g., "Tell me more about that")
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

# QA prompt: Instructs the LLM to answer strictly based on retrieved document context
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a strict document question answering assistant.\n\n"
     "CRITICAL INSTRUCTIONS:\n"
     "1. Answer the user's question relying ONLY and EXCLUSIVELY on the provided Context below.\n"
     "2. Do NOT use any pre-existing, external, or real-world knowledge.\n"
     "3. If the answer is NOT explicitly stated in or directly supported by the provided Context, you MUST answer with:\n"
     "\"I don't know, there is no such thing given in these documents.\"\n"
     "4. Never guess, assume, speculate, or bring in outside facts (such as world leaders, general facts, or external entities) if they are not in the Context.\n"
     "5. Keep your response direct, factual, and strictly faithful to the provided text."),
    ("system", "Context:\n{context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])



def _get_llm(model: str):
    """
    Initialize and return the appropriate LLM based on the model name.

    Supports:
        - Groq models (qwen/qwen3.8-27b, openai/gpt-oss-120b)
        - HuggingFace Hub models (google/flan-t5-large, mistralai/Mistral-7B-Instruct-v0.1)
        - OpenAI models as fallback (gpt-4o, gpt-4o-mini)

    Args:
        model: Model identifier string

    Returns:
        A LangChain-compatible LLM instance
    """
    groq_models = [
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-120b"
    ]

    if model in groq_models or "qwen" in model.lower() or "gpt-oss" in model.lower():
        groq_api_key = os.getenv("GROQ_API_KEY")
        if groq_api_key:
            from langchain_groq import ChatGroq
            logger.info(f"Using Groq model: {model}")
            return ChatGroq(model=model, groq_api_key=groq_api_key, temperature=0.0)
        else:
            logger.warning("GROQ_API_KEY not set.")

    huggingface_models = [
        "google/flan-t5-large",
        "mistralai/Mistral-7B-Instruct-v0.1"
    ]

    if model in huggingface_models:
        hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        if hf_token:
            from langchain_huggingface import HuggingFaceEndpoint
            logger.info(f"Using HuggingFace model: {model}")
            return HuggingFaceEndpoint(
                repo_id=model,
                huggingfacehub_api_token=hf_token,
                temperature=0.01,
                max_new_tokens=512
            )
        else:
            logger.warning("HUGGINGFACEHUB_API_TOKEN not set. Falling back to OpenAI.")
            model = "gpt-4o-mini"

    # OpenAI fallback
    from langchain_openai import ChatOpenAI
    logger.info(f"Using OpenAI model: {model}")
    return ChatOpenAI(model=model, temperature=0.0)



def get_rag_chain(model: str = "google/flan-t5-large"):
    """
    Build and return the complete RAG chain.

    Architecture:
        1. History-Aware Retriever: Reformulates the user's question using chat history,
           then retrieves relevant document chunks from FAISS.
        2. Stuff Documents Chain: Combines retrieved chunks into the LLM prompt context.
        3. Retrieval Chain: Orchestrates the full pipeline from query to answer.

    Args:
        model: The LLM model identifier to use for generation

    Returns:
        A LangChain retrieval chain ready for invocation

    Raises:
        ValueError: If no FAISS index is available (no documents uploaded)
    """
    retriever = get_retriever()
    if retriever is None:
        raise ValueError(
            "No documents have been indexed yet. "
            "Please upload documents before querying."
        )

    llm = _get_llm(model)

    # Step 1: Create a history-aware retriever
    # This reformulates follow-up questions into standalone queries
    # before performing similarity search in the FAISS index
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    # Step 2: Create the question-answering chain
    # Uses "stuff" strategy — all retrieved documents are concatenated
    # into a single context string passed to the LLM
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    # Step 3: Combine into a full retrieval chain
    rag_chain = create_retrieval_chain(
        history_aware_retriever, question_answer_chain
    )

    return rag_chain