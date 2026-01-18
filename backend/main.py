from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload, chat

app = FastAPI(title="Academic RAG API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "Academic RAG API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
