import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from dotenv import load_dotenv

FAISS_INDEX_PATH = "vectorstore/faiss_index"

# Global cache — model loaded once, reused
_embedding_model = None
_vector_store = None

def get_embedding_model():
    """Lazy load — only loads model when first called, not at import time."""
    global _embedding_model
    if _embedding_model is None:
        from langchain_huggingface import HuggingFaceEmbeddings
        _embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    return _embedding_model

def load_vector_store():
    """Lazy load vector store from disk."""
    global _vector_store
    if _vector_store is not None:
        return _vector_store
    embeddings = get_embedding_model()
    if os.path.exists(FAISS_INDEX_PATH):
        _vector_store = FAISS.load_local(
            FAISS_INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
        return _vector_store
    else:
        return build_vector_store()

def build_vector_store():
    """Builds FAISS index from knowledge base. Run once."""
    from vectorstore.knowledge_base import KNOWLEDGE_BASE_DOCUMENTS
    global _vector_store
    print("Building knowledge base vector store...")
    docs = [Document(page_content=text.strip()) for text in KNOWLEDGE_BASE_DOCUMENTS]
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(docs)
    embeddings = get_embedding_model()
    _vector_store = FAISS.from_documents(chunks, embeddings)
    _vector_store.save_local(FAISS_INDEX_PATH)
    print(f"Vector store saved to {FAISS_INDEX_PATH}")
    return _vector_store

def retrieve_relevant_knowledge(query: str, k: int = 3) -> str:
    """Searches knowledge base for relevant chunks."""
    try:
        vector_store = load_vector_store()
        relevant_docs = vector_store.similarity_search(query, k=k)
        return "\n\n---\n\n".join([doc.page_content for doc in relevant_docs])
    except Exception as e:
        print(f"RAG retrieval failed: {e}")
        return ""
