
from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredHTMLLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from typing import List, Optional
import os
import logging

logger = logging.getLogger(__name__)


EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

embedding_function = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL_NAME,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}  # Normalize for cosine similarity
)


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""],
    is_separator_regex=False
)


FAISS_INDEX_DIR = "./faiss_index"

def _get_vectorstore() -> Optional[FAISS]:
    """
    Load the persisted FAISS index from disk.
    Returns None if no index exists yet (first run).
    """
    if os.path.exists(FAISS_INDEX_DIR):
        try:
            return FAISS.load_local(
                FAISS_INDEX_DIR,
                embedding_function,
                allow_dangerous_deserialization=True
            )
        except Exception as e:
            logger.warning(f"Failed to load FAISS index: {e}. Starting with empty index.")
            return None
    return None

def _save_vectorstore(vectorstore: FAISS) -> None:
    """Persist the FAISS index to disk for durability."""
    vectorstore.save_local(FAISS_INDEX_DIR)
    logger.info(f"FAISS index saved to {FAISS_INDEX_DIR}")



def load_and_split_document(file_path: str) -> List[Document]:
    """
    Load a document from the given file path and split it into optimized chunks.

    Supports: PDF (.pdf), Word (.docx), HTML (.html), Plain Text (.txt)

    Args:
        file_path: Path to the document file

    Returns:
        List of Document chunks with metadata

    Raises:
        ValueError: If the file type is not supported
    """
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.pdf':
        loader = PyPDFLoader(file_path)
    elif file_extension == '.docx':
        loader = Docx2txtLoader(file_path)
    elif file_extension == '.html':
        loader = UnstructuredHTMLLoader(file_path)
    elif file_extension == '.txt':
        loader = TextLoader(file_path, encoding='utf-8')
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

    documents = loader.load()
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Loaded {file_path}: {len(documents)} pages → {len(chunks)} chunks")
    return chunks



def index_document_to_faiss(file_path: str, file_id: int) -> bool:
    """
    Load, chunk, embed, and index a document into the FAISS vector store.

    Pipeline: File → Loader → Text Splitter → HuggingFace Embeddings → FAISS Index

    Args:
        file_path: Path to the document file
        file_id: Unique identifier for tracking the document in the vector store

    Returns:
        True if indexing succeeded, False otherwise
    """
    try:
        splits = load_and_split_document(file_path)

        # Attach file_id metadata to each chunk for retrieval and deletion
        for split in splits:
            split.metadata['file_id'] = file_id

        # Load existing index or create new one
        existing_store = _get_vectorstore()

        if existing_store is not None:
            # Merge new documents into existing FAISS index
            existing_store.add_documents(splits)
            _save_vectorstore(existing_store)
        else:
            # Create a new FAISS index from the first set of documents
            new_store = FAISS.from_documents(splits, embedding_function)
            _save_vectorstore(new_store)

        logger.info(f"Successfully indexed {len(splits)} chunks for file_id={file_id}")
        return True

    except Exception as e:
        logger.error(f"Error indexing document (file_id={file_id}): {e}")
        return False


def delete_doc_from_faiss(file_id: int) -> bool:
    """
    Delete all chunks belonging to a specific document from the FAISS index.

    Since FAISS doesn't natively support metadata-based deletion, this rebuilds
    the index excluding chunks with the specified file_id.

    Args:
        file_id: The file_id of the document to remove

    Returns:
        True if deletion succeeded, False otherwise
    """
    try:
        vectorstore = _get_vectorstore()
        if vectorstore is None:
            logger.warning(f"No FAISS index found. Nothing to delete for file_id={file_id}")
            return True

        # Extract all documents from the current index
        all_docs = vectorstore.docstore._dict
        remaining_docs = []

        for doc_id, doc in all_docs.items():
            if doc.metadata.get('file_id') != file_id:
                remaining_docs.append(doc)

        deleted_count = len(all_docs) - len(remaining_docs)
        logger.info(f"Removing {deleted_count} chunks for file_id={file_id}")

        if remaining_docs:
            # Rebuild the FAISS index with remaining documents
            new_store = FAISS.from_documents(remaining_docs, embedding_function)
            _save_vectorstore(new_store)
        else:
            # No documents remain — remove the index directory
            import shutil
            if os.path.exists(FAISS_INDEX_DIR):
                shutil.rmtree(FAISS_INDEX_DIR)
            logger.info("All documents removed. FAISS index cleared.")

        return True

    except Exception as e:
        logger.error(f"Error deleting document (file_id={file_id}) from FAISS: {e}")
        return False


def get_retriever(search_kwargs: dict = None):
    """
    Get a FAISS-backed retriever for the RAG chain.

    Uses similarity search with k=3 nearest neighbors (tuned from k=2
    for improved recall without sacrificing precision).

    Args:
        search_kwargs: Optional override for search parameters

    Returns:
        A LangChain retriever backed by the FAISS index, or None if no index exists
    """
    if search_kwargs is None:
        search_kwargs = {"k": 3}

    vectorstore = _get_vectorstore()
    if vectorstore is None:
        logger.warning("No FAISS index available. Upload documents first.")
        return None

    return vectorstore.as_retriever(search_kwargs=search_kwargs)
