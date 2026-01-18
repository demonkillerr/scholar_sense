from fastapi import APIRouter, UploadFile, File, HTTPException
from services.pdf_processor import PDFProcessor
from services.rag_service import RAGService
from config import settings
import os
import shutil

router = APIRouter()
pdf_processor = PDFProcessor()
rag_service = RAGService()


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF document"""
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Save uploaded file
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process PDF
        documents = pdf_processor.extract_text_with_metadata(file_path)
        chunks = pdf_processor.chunk_documents(documents)
        
        # Create/update vector store
        rag_service.create_vectorstore(chunks, file.filename)
        
        return {
            "message": "PDF uploaded and processed successfully",
            "filename": file.filename,
            "pages": len(documents),
            "chunks": len(chunks)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@router.get("/documents")
async def list_documents():
    """List all uploaded documents"""
    try:
        files = os.listdir(settings.UPLOAD_DIR)
        pdf_files = [f for f in files if f.endswith('.pdf')]
        return {"documents": pdf_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")
