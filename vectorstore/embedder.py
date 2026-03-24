import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

FAISS_INDEX_PATH = "vectorstore/faiss_index"
_vector_store = None
_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
    return _embedding_model

def load_vector_store():
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
    return None

def retrieve_relevant_knowledge(query: str, k: int = 3) -> str:
    try:
        vector_store = load_vector_store()
        if vector_store is None:
            return ""
        relevant_docs = vector_store.similarity_search(query, k=k)
        return "\n\n---\n\n".join([doc.page_content for doc in relevant_docs])
    except Exception as e:
        print(f"RAG retrieval failed: {e}")
        return ""
