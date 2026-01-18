from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.rag_service import RAGService

router = APIRouter()
rag_service = RAGService()


class ChatRequest(BaseModel):
    keyword: str
    document_name: str = None


@router.post("/chat")
async def chat(request: ChatRequest):
    """Analyze sentiment of research paper against a keyword"""
    try:
        if not request.keyword:
            raise HTTPException(status_code=400, detail="Keyword is required")
        
        # Perform sentiment analysis
        result = rag_service.analyze_sentiment(
            keyword=request.keyword,
            document_name=request.document_name
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing sentiment: {str(e)}")
