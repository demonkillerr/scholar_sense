from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from typing import List, Dict
from config import settings
import os


class RAGService:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=settings.GOOGLE_API_KEY
        )
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.3
        )
        self.vectorstore = None
        self.collection_name = "academic_papers"

    def create_vectorstore(self, chunks: List[Dict], document_name: str):
        """Create or update vector store with document chunks"""
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [
            {
                "page_number": chunk["page_number"],
                "section": chunk["section"],
                "chunk_index": chunk["chunk_index"],
                "citations": ", ".join(chunk["citations"]),
                "document_name": document_name
            }
            for chunk in chunks
        ]
        
        # Create or update Chroma vectorstore
        if self.vectorstore is None:
            self.vectorstore = Chroma.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas,
                collection_name=self.collection_name,
                persist_directory=settings.CHROMA_DB_PATH
            )
        else:
            self.vectorstore.add_texts(
                texts=texts,
                metadatas=metadatas
            )

    def load_vectorstore(self):
        """Load existing vector store"""
        if os.path.exists(settings.CHROMA_DB_PATH):
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=settings.CHROMA_DB_PATH
            )

    def analyze_sentiment(self, keyword: str, document_name: str = None) -> Dict:
        """Analyze sentiment of paper towards a keyword with citations"""
        if self.vectorstore is None:
            self.load_vectorstore()
        
        # Build search query
        search_query = f"What is discussed about {keyword}? Include any mentions, opinions, or findings related to {keyword}."
        
        # Retrieve relevant chunks
        if document_name:
            results = self.vectorstore.similarity_search(
                search_query,
                k=settings.TOP_K_RESULTS,
                filter={"document_name": document_name}
            )
        else:
            results = self.vectorstore.similarity_search(
                search_query,
                k=settings.TOP_K_RESULTS
            )
        
        if not results:
            return {
                "sentiment": "No information found",
                "summary": f"No relevant information found about '{keyword}' in the document.",
                "evidence": []
            }
        
        # Prepare context with citations
        context_parts = []
        evidence = []
        
        for doc in results:
            metadata = doc.metadata
            citation_info = f"(Page {metadata['page_number']}, {metadata['section']})"
            context_parts.append(f"{doc.page_content}\n{citation_info}")
            
            evidence.append({
                "text": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "page_number": metadata['page_number'],
                "section": metadata['section'],
                "citations": metadata.get('citations', '')
            })
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Create prompt for sentiment analysis
        prompt = PromptTemplate(
            template="""You are analyzing an academic research paper. Based on the following excerpts from the paper, 
analyze the sentiment and stance towards the keyword: "{keyword}".

Context from the paper:
{context}

Provide a comprehensive analysis with the following structure:
**Overall Sentiment:** [State clearly: Positive, Negative, Neutral, or Mixed]

Then provide:
1. A summary of how the paper discusses this topic
2. Key claims or findings

Be specific and reference the page numbers when making claims.

Analysis:""",
            input_variables=["keyword", "context"]
        )
        
        # Get LLM response
        formatted_prompt = prompt.format(keyword=keyword, context=context)
        response = self.llm.invoke(formatted_prompt)
        
        # Parse response - handle both string and list content
        if isinstance(response.content, list):
            analysis_text = response.content[0].get('text', '') if response.content else ''
        else:
            analysis_text = response.content
        
        # Extract sentiment (improved parsing - look for the entire text)
        sentiment = "Neutral"
        analysis_lower = analysis_text.lower() if isinstance(analysis_text, str) else ''
        
        # Look for sentiment indicators throughout the text, with priority to earlier mentions
        if "sentiment: positive" in analysis_lower or "sentiment:** positive" in analysis_lower:
            sentiment = "Positive"
        elif "sentiment: negative" in analysis_lower or "sentiment:** negative" in analysis_lower:
            sentiment = "Negative"
        elif "sentiment: mixed" in analysis_lower or "sentiment:** mixed" in analysis_lower:
            sentiment = "Mixed"
        elif "sentiment: neutral" in analysis_lower or "sentiment:** neutral" in analysis_lower:
            sentiment = "Neutral"
        # Fallback: check first 500 chars for keywords
        elif "positive" in analysis_lower[:500] and "negative" not in analysis_lower[:500]:
            sentiment = "Positive"
        elif "negative" in analysis_lower[:500] and "positive" not in analysis_lower[:500]:
            sentiment = "Negative"
        elif "positive" in analysis_lower[:500] and "negative" in analysis_lower[:500]:
            sentiment = "Mixed"
        
        return {
            "sentiment": sentiment,
            "summary": analysis_text,
            "evidence": evidence
        }
