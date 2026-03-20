import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from vectorstore.knowledge_base import KNOWLEDGE_BASE_DOCUMENTS
from dotenv import load_dotenv

FAISS_INDEX_PATH = "vectorstore/faiss_index"

def get_embedding_model(): #HuggingFaceEmbeddings loads a model from HuggingFace that converts text to vectors. The model all-MiniLM-L6-v2 is the industry standard for RAG applications.
    # The first time you run this model, it downloads the model from HuggingFace — about 80MB

    """
    Loads the Huggingface embedding model.
    This model converts text into vectors.
    Using all -MiniLM-L6-v2 because:
    - Free and runs locally - no API cost
    - Fast - small model, quick inference
    - Good quality for semantic search tasks
    - Industry standard for RAG applications
    
    """
    return HuggingFaceEmbeddings(
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
    )
    
    
def build_vector_store():
    """
    Builds the FAISS vector store from knowledge base documents.
    Run this once to create the index.
    Save to disk so it does not rebuild everytime app starts.
    
    Steps:
    1. Convert raw strings to Document objects
    2. Split documents into chunks
    3. Convert chunks to vectors using embedding model
    4. Store vectors in FAISS
    5. Save FAISS index to disk
    """
    
    print("Building knowledge base vector store...")
    
    #Converting documents to Document objects
    docs = [Document(page_content= text.strip()) #LangChain works with Document objects — not raw strings. This line converts your list of strings into Document objects. .strip() removes leading and trailing whitespace.
            for text in KNOWLEDGE_BASE_DOCUMENTS]
    
    #The text splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size= 500,
        chunk_overlap = 50,
        separators=["\n\n", "\n", ".", " "]
    )
    
    chunks = splitter.split_documents(docs)
    print(f"Created{len(chunks)} chunks from {len(docs)} documents")
    
    embeddings = get_embedding_model()
    
    print("Converting chunks to vectors ....(first time takes 1-2 minutes)")
    
    
    #Building the FAISS index
    vector_store = FAISS.from_documents(chunks, embeddings)  #FAISS.from_documents() takes every chunk, converts it to a vector using your embedding model, and stores all vectors in a FAISS index — an optimised data structure for finding similar vectors fast.       
    
    vector_store.save_local(FAISS_INDEX_PATH) #save_local() saves the index to disk as files in vectorstore/faiss_index/. This means you only build it once. Every subsequent app start loads from disk — much faster than rebuilding.
    print(f"Vector store saved to {FAISS_INDEX_PATH}")

    return vector_store

#Loading the vector store
#Checks if the index already exists on disk. If yes — loads it. If no — builds it fresh. allow_dangerous_deserialization=True is required by FAISS when loading locally saved indexes — it is safe for your own files.
def load_vector_store():
    """ 
    Loads existing FAISS indexfrom disk.
    Much faster than rebuilding - use this on every app start.
    Builds fresh if index does not exist yet.
    
    
    """
    
    embeddings = get_embedding_model()
    
    if os.path.exists(FAISS_INDEX_PATH):
        vector_store = FAISS.load_local(
            FAISS_INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
        return vector_store
    else:
        return build_vector_store()
 
 #The retrieval function   
 
 #This is called on every user question. Here is exactly what happens:
#similarity_search(query, k=3) — converts the query to a vector, finds the 3 chunks whose vectors are most similar, returns them as Document objects.
#"\n\n---\n\n".join(...) — joins the 3 chunks into one string with a separator between them. This combined string gets injected into Claude's prompt as retrieved context.
#k: int = 3 — default value of 3. The = 3 means if you call retrieve_relevant_knowledge("question") without specifying k, it returns 3 chunks. You can override with retrieve_relevant_knowledge("question", k=5) to get 5.
def retrieve_relevant_knowledge(query: str, k: int = 3) -> str:
    """ 
    Searches the knowledge base for the most relevant chunks.
    Called on every user question in the chat agent.
    
    Input : user's question as a string
    Output : top k most relevant chunks joined as one string
    
    This string gets injected into Claude's prompt as context.
    Claude answers from this retrieved knowledge — not hallucination.
    
    
    
    """
    
    
    vector_store = load_vector_store()
    
    relevant_docs = vector_store.similarity_search(query, k=k)
    knowledge_context = "\n\n---\n\n".join(
        [doc.page_content for doc in relevant_docs]
    )
    
    return knowledge_context


if __name__ == "__main__":
    print("Building vector store from knowledge base...")
    build_vector_store()
    print()
    print("Testing retrieval...")
    test_query = "How should I write bullet points for a PM resume?"
    result = retrieve_relevant_knowledge(test_query)
    print(f"Query: {test_query}")
    print()
    print("Retrieved knowledge:")
    print(result)
       
            
        
    
    