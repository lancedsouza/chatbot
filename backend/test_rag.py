import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA

# 📁 Configurable directories
PDF_DIR = os.getenv("PDF_DIR", "pdfs")
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "faiss_index")

# 📄 Load and split all PDFs
def load_all_pdfs(pdf_dir):
    if not os.path.exists(pdf_dir):
        raise FileNotFoundError(f"PDF directory '{pdf_dir}' not found.")
    
    all_docs = []
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            path = os.path.join(pdf_dir, filename)
            loader = PyPDFLoader(path)
            docs = loader.load()
            all_docs.extend(docs)
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(all_docs)

# 🧠 Build or load FAISS index
def build_or_load_faiss(docs, embeddings):
    index_file = os.path.join(FAISS_INDEX_PATH, "index.faiss")
    if os.path.exists(index_file):
        print("📥 Loading existing FAISS index...")
        return FAISS.load_local(
            FAISS_INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        print("🛠️ Building new FAISS index...")
        db = FAISS.from_documents(docs, embeddings)
        db.save_local(FAISS_INDEX_PATH)
        return db

# 🔄 Initialize RAG components
print("📚 Loading PDFs and building vector index...")
docs = load_all_pdfs(PDF_DIR)
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
db = build_or_load_faiss(docs, embeddings)
retriever = db.as_retriever()

# 🧠 Initialize LLM (Ollama)
llm = OllamaLLM(
    model="mistral",
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
)

# 🔗 Set up the RetrievalQA chain
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

# ❓ Handle incoming questions
def rag_answer(question: str) -> str:
    try:
        print(f"[DEBUG] RAG question received: {question}")
        result = qa_chain.invoke({"query": question})

        # Extract just the answer string
        if isinstance(result, dict) and "result" in result:
            return result["result"]
        return str(result)

    except Exception as e:
        print(f"[ERROR] Failed to answer question: {str(e)}")
        return "❌ Sorry, I couldn't process your question due to an internal error."
