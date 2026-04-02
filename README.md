<div align="center">
  <img src="https://img.icons8.com/color/96/000000/artificial-intelligence.png" alt="Rangkush Logo">
  <h1>Rangkush RAG Dashboard</h1>
  <p><strong>A Next-Generation Retrieval-Augmented Generation (RAG) Web Application</strong></p>
  
  [![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a393.svg)](https://fastapi.tiangolo.com/)
  [![Vite](https://img.shields.io/badge/Vite-Build-646CFF.svg)](https://vitejs.dev/)
  [![LangChain](https://img.shields.io/badge/LangChain-Integration-lightgrey.svg)](https://python.langchain.com/)
</div>

<br/>

## 📖 Overview

**Rangkush** transforms standard local script workflows into a beautiful, fully functional web dashboard. Upload your local `.pdf` and `.txt` files directly onto a modern UI, chunk massive text corpus documents into highly optimized vector embeddings, and dynamically converse with a powerful LLM—all without ever modifying configuration files manually.

## 🚀 How the Project Works

This project is designed to make document interrogating incredibly easy by bridging a powerful LangChain backend with an interactive web UI.
1. **Upload Documents:** Simply drag and drop your PDFs or TXTs. The Python backend reads them seamlessly and splits them into indexable chunks.
2. **Setup Intelligence:** Hook your Groq LLM API Key directly into the dashboard securely.
3. **Chat & Retrieve:** Ask intelligent questions about your documents in real-time. The system intelligently fetches the closest chunk of data using FAISS, parses the context rapidly via Groq's Mixtral Engine, and hands you the summary! 
4. **Transparent Computing:** All native internal Python computing outputs (like loading traces) are streamed into your chat bubble!

## 🏗️ Technical Architecture Workflow

The following execution tree demonstrates the synchronous flow of documents to chunks, and embedding indexing logic against prompt queries:

```mermaid
graph TD;
    %% UI interactions
    A[Frontend Web API]:::ui -->|1. Drag & Drop Upload| B(FastAPI Router)
    
    %% Processing
    B --> C{Intelligent Document Loading}:::logic
    C -->|PDF| D[PyMuPDFLoader]:::logic
    C -->|TXT| D[TextLoader]:::logic
    D --> E(Recursive Character Splitter)
    E --> F[FAISS Memory Core]:::db
    
    %% Semantic DB
    F --- G((HuggingFace all-MiniLM-L6-v2)):::db
    
    %% Query Flow
    A -->|2. Config API Key + Input| H[Retriever Chain]
    F -->|K=3 Semantic Matches| H
    H --> I{Groq LLM Engine}:::llm
    
    %% Output
    I -->|Returns Summaries & Traces| A
    
    %% Styling
    classDef ui fill:#0f172a,stroke:#3b82f6,stroke-width:2px,color:#fff
    classDef logic fill:#1e293b,stroke:#94a3b8,color:#fff
    classDef llm fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#fff
    classDef db fill:#4c1d95,stroke:#a78bfa,color:#fff
```

---

## 🛠️ How to Run Locally (Developer Setup)

If you'd like to clone this project and run it dynamically on your system, follow these steps:

### 1. Clone the Source
```bash
git clone https://github.com/Kushal-prime/RAG-MODEL.git
cd RAG-MODEL
```

### 2. Initialize the Python Core
Ensure that your environment variables are set up accurately and virtual environments are instantiated.
```bash
python -m venv .venv
```
*Activate the Environment:*
*   **Windows**: `.venv\Scripts\activate`
*   **Unix**: `source .venv/bin/activate`

```bash
# Install critical APIs and pipelines
pip install -r requirements-api.txt
pip install -r requirements.txt
```

### 3. Initialize Visual Interface Components
Node.js dependencies must be installed for Vite architecture.
```bash
cd frontend
npm install
```

### 4. Runtime Execution
Start the internal components sequentially. Ensure your environment port mappings correctly align to Localhost.

**Terminal 1 (Backend Core API System)**
```bash
python api.py
```

**Terminal 2 (Frontend Client)**
```bash
cd frontend
npm run dev
```

Browse to your local hosted port environment (Typically `http://localhost:5173/`) and begin talking to your documents!

<br />
<div align="center">
  <p>Maintainer: <b>Himanshu Garse (Kushal-prime)</b></p>
</div>
