import os
import sys
import io
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from langchain_groq import ChatGroq
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Rangkush RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path("Data/uploaded")
DATA_DIR.mkdir(parents=True, exist_ok=True)
FAISS_DIR = "./faiss_db"

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_vectorstore():
    # Only load if the index exists
    if os.path.exists(FAISS_DIR) and os.path.exists(os.path.join(FAISS_DIR, "index.faiss")):
        print("FAISS Index loaded.")
        return FAISS.load_local(FAISS_DIR, embeddings, allow_dangerous_deserialization=True)
    return None

class QueryRequest(BaseModel):
    query: str

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    # Capture standard output 
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    
    try:
        file_path = DATA_DIR / file.filename
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        print(f"File uploaded to {file_path}")
        
        if file.filename.endswith(".pdf"):
            loader = PyMuPDFLoader(str(file_path))
        else:
            loader = TextLoader(str(file_path), encoding="utf-8")
        
        docs = loader.load()
        print(f"Loaded {len(docs)} documents from loader.")
        if docs:
            print(f"Preview: {docs[0].page_content[:200]}...")
            print(f"Metadata: {docs[0].metadata}")
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        splits = text_splitter.split_documents(docs)
        print(f"Splitting done -> {len(splits)} chunks created.")
        
        # Load or create FAISS vectorstore
        vectorstore = get_vectorstore()
        if vectorstore is None:
            print("Creating new FAISS indexing database.")
            vectorstore = FAISS.from_documents(splits, embeddings)
        else:
            print("Adding documents to existing FAISS database.")
            vectorstore.add_documents(documents=splits)
            
        vectorstore.save_local(FAISS_DIR)
        print("Database successfully saved.")
        
        console_output = new_stdout.getvalue()
        sys.stdout = old_stdout
        return {"message": "Success", "chunks": len(splits), "console": console_output}
        
    except Exception as e:
        sys.stdout = old_stdout
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query")
async def query_collection(payload: QueryRequest, request: Request):
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    
    try:
        print(f"User Query Received: {payload.query}")
        vectorstore = get_vectorstore()
        if not vectorstore:
            sys.stdout = old_stdout
            return {"answer": "No documents uploaded yet! Please upload a PDF or text file first."}
            
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        # Check custom header first
        groq_api_key = request.headers.get("x-groq-api-key") or os.environ.get("GROQ_API_KEY")
        
        if groq_api_key:
            print("Using Groq API for LLM generation.")
            llm = ChatGroq(temperature=0.3, model_name="mixtral-8x7b-32768", groq_api_key=groq_api_key)
            prompt = ChatPromptTemplate.from_template(
                """Answer the following question based only on the provided context:
                <context>
                {context}
                </context>
                Question: {input}"""
            )
            document_chain = create_stuff_documents_chain(llm, prompt)
            retrieval_chain = create_retrieval_chain(retriever, document_chain)
            
            response = retrieval_chain.invoke({"input": payload.query})
            answer = response["answer"]
        else:
            print("No GROQ_API_KEY found, providing raw context search results.")
            docs = retriever.invoke(payload.query)
            context = "\n\n".join([d.page_content for d in docs])
            answer = f"[No GROQ_API_KEY set. Showing retrieval fallback.]\n\nContext found:\n{context}"
            
        console_output = new_stdout.getvalue()
        sys.stdout = old_stdout
        
        # Combine command output with answer
        final_answer = "💻 Terminal Output:\n```text\n" + console_output + "\n```\n\n📝 Analysis:\n" + answer
        
        return {"answer": final_answer}
    except Exception as e:
        print("Query error:", e)
        sys.stdout = old_stdout
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
