# Academic RAG Application

A full-stack Retrieval-Augmented Generation (RAG) application for sentiment analysis of academic research papers.

## Features

- 📄 **PDF Upload**: Upload academic research papers in PDF format
- 🔍 **Sentiment Analysis**: Analyze paper sentiment towards specific keywords
- 📚 **Citation Support**: Extract and display citations with page references
- 💬 **Interactive Chat**: Query-based interface for analysis
- 🎨 **Modern UI**: Next.js with Tailwind CSS

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

4. The `.env` file is already configured with your API key. Verify settings:
```
GOOGLE_API_KEY=AIzaSyCSxhnZqtSYz74xzxD4FnnoiIfbgfNx3S4
CHROMA_DB_PATH=./chroma_db
UPLOAD_DIR=./uploads
```

5. Start the FastAPI server:
```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

### Frontend Setup

1. Open a new terminal and navigate to frontend directory:
```powershell
cd frontend
```

2. Install dependencies:
```powershell
npm install
```

3. The `.env.local` file is already configured. Verify:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Start the development server:
```powershell
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

1. **Upload a PDF**:
   - Open `http://localhost:3000`
   - Go to "Upload Document" tab
   - Drag and drop or browse for a PDF research paper
   - Click "Upload and Process"

2. **Analyze Sentiment**:
   - Switch to "Sentiment Analysis" tab
   - Enter a keyword (e.g., "machine learning", "climate change")
   - Optionally select a specific document
   - Click "Analyze Sentiment"

3. **View Results**:
   - Overall sentiment classification
   - Detailed analysis summary
   - Supporting evidence with page numbers and citations

## API Endpoints

### `POST /api/upload`
Upload and process a PDF document
- **Request**: `multipart/form-data` with PDF file
- **Response**: Processing status and metadata

### `POST /api/chat`
Analyze sentiment for a keyword
- **Request**: `{ "keyword": "string", "document_name": "string" }`
- **Response**: Sentiment analysis with citations

### `GET /api/documents`
List all uploaded documents
- **Response**: Array of document filenames

## How It Works

1. **PDF Processing**:
   - Extracts text from PDF with page numbers
   - Identifies sections (Abstract, Introduction, etc.)
   - Splits into chunks with metadata

2. **Embedding & Storage**:
   - Generates embeddings using Google's embedding model
   - Stores in ChromaDB vector database
   - Preserves citation and location metadata

3. **Sentiment Analysis**:
   - Retrieves relevant chunks based on keyword
   - Sends context to Gemini for analysis
   - Returns sentiment with supporting evidence

4. **Citation Extraction**:
   - Pattern-based detection of citations: `[1]`, `(Author, Year)`
   - Links citations to page numbers and sections
   - Displays in user-friendly format

## Configuration

### Backend (`backend/config.py`)
- `CHUNK_SIZE`: Text chunk size (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)
- `TOP_K_RESULTS`: Number of results to retrieve (default: 5)

### Environment Variables
- `GOOGLE_API_KEY`: Google Gemini API key
- `CHROMA_DB_PATH`: Vector database location
- `UPLOAD_DIR`: PDF upload directory

## Troubleshooting

### Backend Issues
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is available
- Verify Google API key is valid

### Frontend Issues
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check if port 3000 is available
- Ensure backend is running before starting frontend

### PDF Processing
- Ensure PDFs are text-based (not scanned images)
- Check file size (large PDFs may take longer to process)

## Future Enhancements

- [ ] Support for multiple document comparison
- [ ] Advanced citation parsing with bibliography extraction
- [ ] Export analysis results to PDF/Word
- [ ] User authentication and document management
- [ ] Support for other document formats (DOCX, TXT)

## License

MIT

## Credits

Built with:
- FastAPI, LangChain, ChromaDB
- Google Gemini API
- Next.js, Tailwind CSS
- PyMuPDF, pdfplumber
