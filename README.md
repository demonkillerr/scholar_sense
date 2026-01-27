# Scholar Sense

A full-stack Retrieval-Augmented Generation (RAG) application for sentiment analysis of academic research papers.

## Features

- **PDF Upload**: Upload academic research papers in PDF format
- **Sentiment Analysis**: Analyze paper sentiment towards specific keywords
- **Citation Support**: Extract and display citations with page references
- **Interactive Chat**: Query-based interface for analysis
- **Modern UI**: Next.js with Tailwind CSS

## Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **LangChain**: RAG pipeline orchestration
- **ChromaDB**: Vector database for embeddings
- **Google Gemini**: LLM for analysis
- **PyMuPDF & pdfplumber**: PDF processing

### Frontend
- **Next.js 14**: React framework with App Router
- **Tailwind CSS**: Utility-first styling
- **TypeScript**: Type-safe development
- **Axios**: HTTP client

## Project Structure

```
windows-build/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables
│   ├── routers/
│   │   ├── upload.py          # PDF upload endpoints
│   │   └── chat.py            # Chat/analysis endpoints
│   ├── services/
│   │   ├── pdf_processor.py   # PDF extraction and chunking
│   │   └── rag_service.py     # RAG pipeline and LLM
│   ├── uploads/               # Uploaded PDFs (auto-created)
│   └── chroma_db/             # Vector database (auto-created)
│
└── frontend/
    ├── app/
    │   ├── layout.tsx         # Root layout
    │   ├── page.tsx           # Main page with tabs
    │   └── globals.css        # Global styles
    ├── components/
    │   ├── UploadTab.tsx      # Upload interface
    │   └── ChatTab.tsx        # Chat interface
    ├── package.json
    ├── tsconfig.json
    ├── tailwind.config.js
    └── next.config.js
```

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- Google API Key (for Gemini)

### Backend Setup

1. Navigate to backend directory:
```powershell
cd backend
```

2. Create a virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

3. Install dependencies:
```powershell
pip install -r requirements.txt
```