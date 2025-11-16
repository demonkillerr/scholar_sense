# ScholarSense Backend

## Overview
RAG-powered backend for academic paper analysis using Flask, ChromaDB, and Google Gemini.

## Features
- **PDF Processing**: Extract structured content from academic PDFs using GROBID
- **Vector Search**: Store and retrieve document embeddings with ChromaDB  
- **RAG Pipeline**: Question answering with citation grounding
- **Multi-Paper Comparison**: Compare methodologies, results, and conclusions
- **RESTful API**: Clean API for frontend integration

## Architecture
```
┌──────────────┐
│   Flask API  │
└──────┬───────┘
       │
   ┌───┴────┬────────┬──────────┐
   ▼        ▼        ▼          ▼
GROBID   ChromaDB  Gemini  Embeddings
(PDF)    (Vector)  (LLM)   (BGE)
```

## Prerequisites
- Python 3.10+
- GROBID service running on port 8070
- Google Gemini API key

## Installation

### 1. Install Dependencies
```bash
cd apps/backend
pip install -r requirements.txt
```

### 2. Download NLTK Data (first time only)
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 4. Start GROBID
```bash
# Using Docker
docker pull lfoppiano/grobid:0.8.0
docker run -d -p 8070:8070 lfoppiano/grobid:0.8.0
```

## Running the Backend

### Development
```bash
export GEMINI_API_KEY="your_key_here"
python app.py
```

### Production
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Documentation
See [API_DOCS.md](./API_DOCS.md) for complete API reference.

## Quick Start

```bash
# 1. Upload a paper
curl -X POST http://localhost:5000/upload \
  -F "file=@paper.pdf"

# 2. Query the paper
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main contribution?"}'

# 3. List papers
curl http://localhost:5000/papers
```

## Core Modules

### `rag_engine.py`
Main RAG pipeline orchestrator. Handles:
- Document chunking
- Embedding generation
- Vector storage
- Query processing
- Answer generation

### `vector_store.py`
ChromaDB wrapper for vector operations:
- Add documents with embeddings
- Semantic search
- Paper management

### `embeddings.py`
Embedding generation using BGE-large-en-v1.5:
- Text encoding
- Query encoding with instruction prefix
- Batch processing

### `llm_client.py`
Google Gemini API integration:
- Citation-grounded Q&A
- Multi-paper comparison
- Stance detection

### `document_processor.py`
PDF processing with GROBID:
- Structured extraction (title, authors, sections)
- Section identification
- Metadata extraction

### `grobid_client.py`
GROBID API client:
- Full-text PDF processing
- TEI XML parsing
- Section extraction

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | - | **Required** Google Gemini API key |
| `GROBID_URL` | `http://localhost:8070` | GROBID service URL |
| `UPLOAD_FOLDER` | `uploads` | Upload directory |
| `VECTOR_STORE_PATH` | `./chroma_db` | ChromaDB storage path |
| `EMBEDDING_MODEL` | `BAAI/bge-large-en-v1.5` | Embedding model |
| `PORT` | `5000` | Flask port |
| `DEBUG` | `False` | Debug mode |

## Testing

```bash
# Run tests
python -m pytest test/

# Test specific endpoint
python test/test_upload_file.py
```

## Troubleshooting

### GROBID Not Available
```bash
# Check GROBID status
curl http://localhost:8070/api/version

# Restart GROBID if needed
docker restart <grobid-container-id>
```

### ChromaDB Issues
```bash
# Clear vector database
rm -rf ./chroma_db
# Backend will recreate on next start
```

### Gemini API Errors
- Verify API key in `.env`
- Check API quota/limits
- Ensure billing is enabled

## Directory Structure
```
apps/backend/
├── app.py                 # Main Flask application
├── rag_engine.py          # RAG pipeline
├── vector_store.py        # ChromaDB wrapper
├── embeddings.py          # Embedding generation
├── llm_client.py          # Gemini API client
├── document_processor.py  # PDF processing
├── grobid_client.py       # GROBID API client
├── requirements.txt       # Python dependencies
├── .env.example           # Example environment config
├── uploads/               # Uploaded PDFs
├── chroma_db/             # Vector database
└── logs/                  # Application logs
```

## Development Tips

1. **First Run**: The embedding model (~1.3GB) will download on first use
2. **Memory**: Recommend 8GB+ RAM for embedding model and vector store
3. **GROBID**: Must be running before uploading papers
4. **API Key**: Get Gemini API key from https://makersuite.google.com/app/apikey
