import os
from langchain_community.vectorstores import FAISS

FAISS_INDEX_PATH = "vectorstore/faiss_index"
_vector_store = None
_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            _embedding_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True}
            )
        except Exception as e:
            print(f"Embedding model failed to load: {e}")
            return None
    return _embedding_model

def load_vector_store():
    global _vector_store
    if _vector_store is not None:
        return _vector_store
    try:
        embeddings = get_embedding_model()
        if embeddings is None:
            return None
        if os.path.exists(FAISS_INDEX_PATH):
            _vector_store = FAISS.load_local(
                FAISS_INDEX_PATH,
                embeddings,
                allow_dangerous_deserialization=True
            )
            return _vector_store
    except Exception as e:
        print(f"Vector store failed to load: {e}")
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
