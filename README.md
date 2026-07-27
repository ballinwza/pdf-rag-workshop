# 📚 RAG system application
![Streamlit](https://img.shields.io/badge/streamlit-009688?style=for-the-badge&logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)
![Render](https://img.shields.io/badge/render-000000?style=for-the-badge&logo=render&logoColor=white)
![Docker](https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

A Tranformer of PDF document and image to text for an Q&A application using Retrieval-Augmented Generation (RAG), powered by Google Gemini API, Pinecone Vector Database, and Streamlit.

## Preview
Deployed on Render it's severless must waiting about 1-3mins after open web site.

* [Backend web demo](https://pdf-rag-workshop.onrender.com/docs) <- Must open service 1st, it's serverless
* [Frontend web demo](https://rag-chatbot-pdf.lovable.app)

## 🌟 Key Features
* 📄 PDF Processing & Chunking: Parses PDF files and chunks content into smaller segments, automatically capturing page number metadata, redacted system for secure information example PDPA.

* 🧩 Image Processing & Chunking: Parses iamge files and chunks content into smaller segments, automatically capturing text to metadata, redacted system for secure information example PDPA.

* 🧠 Vector Embeddings: Converts text into 768-dimensional vector embeddings using Gemini's gemini-embedding-001 model.

* 🌲 Vector Search: Retrieves the most relevant context using cosine similarity on Pinecone Serverless Vector DB.

* 💬 Context-Aware Q&A Chat: Delivers accurate answers based on document context with exact page citations to prevent hallucinations.

* 📝 Multi-Namespace RAG: Individual information each RAG generate answer from data in namespace.

## 🛠️ Technology
| Systems  | Dependencies | Jobs  | 
|---|---|---|
| UI  | Streamlit (for test) & frontend web service  | UI interface  |
| PDF Extraction  | PyPDF + Langchain Text Splitter  | Convert PDF to text  |
| Optical Character Recognition  |  Google vision  | Convert image to text  |
| Redaction  | Sanitizer service  | Redacted secure information  |
| Embedding Mode  | gemini-embedding-001  | Vector with 768 dimensions  |
| Vector Database | Pinecone Serverless Index | Vector data storing and similary search
| LLM Model | gemini-3.5-flash-lite | Analystor question and answer

## 📂 Project Structure
```
pdf-rag-workshop/
│
├── src/                  # Main api service
│   ├── config.py         # Configuration & Environment Variables
│   ├── models            # Request & response model
│   ├── repositories      # Connector outside environemnt
│   ├── services          # Logic
│   ├── routers           # Api route
├── main.py               # API configuration
└── app.py                # Streamlit UI
```

## 🚀 Setup & Usage (Local)
1. Install Makefile 
[Docs](https://makefiletutorial.com/) ,
[Download windows](https://gnuwin32.sourceforge.net/packages/make.htm)

2. Open Virtual Environment
macOS/Linux: source venv/bin/activate
Windows (PowerShell): .\venv\Scripts\Activate.ps1

3. Create ```.env``` and fill all variable follow ```.env.template```

4. Call this command sequently```$make before-init``` ```$make init``` ```$make run```

5. Web browser will open ```http://localhost:8501``` automaticly

## 🚀 Usage (Docker)
1. Create ```.env``` and fill all variable follow ```.env.template```

2. ```docker-compose up```

## 🔄 Apllication Workflow (Streamlit)
1. Upload PDF documents on Sidebar

2. Asking question about PDF directly on __Tab2__

3. Quick summarize PDF on __Tab3__

## System Architecture Diagram
![alt text](guide/data-flow.jpg)