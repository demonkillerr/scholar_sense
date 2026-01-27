import fitz  # PyMuPDF
import pdfplumber
import re
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import settings


class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def extract_text_with_metadata(self, pdf_path: str) -> List[Dict]:
        """Extract text from PDF with page numbers and section information"""
        documents = []
        
        # Use PyMuPDF for text extraction
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            if text.strip():
                # Try to identify section headers
                section = self._identify_section(text)
                
                documents.append({
                    "text": text,
                    "page_number": page_num + 1,
                    "section": section
                })
        
        doc.close()
        return documents

    def _identify_section(self, text: str) -> str:
        """Simple section header identification"""
        # Look for common academic paper sections
        lines = text.split('\n')
        for line in lines[:5]:  # Check first few lines
            line_clean = line.strip().upper()
            if any(keyword in line_clean for keyword in [
                'ABSTRACT', 'INTRODUCTION', 'METHODOLOGY', 'METHODS',
                'RESULTS', 'DISCUSSION', 'CONCLUSION', 'REFERENCES'
            ]):
                return line.strip()
        return "Unknown Section"

    def chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        """Split documents into chunks while preserving metadata"""
        all_chunks = []
        
        for doc in documents:
            text = doc["text"]
            chunks = self.text_splitter.split_text(text)
            
            for i, chunk in enumerate(chunks):
                all_chunks.append({
                    "text": chunk,
                    "page_number": doc["page_number"],
                    "section": doc["section"],
                    "chunk_index": i,
                    "citations": self._extract_citations(chunk)
                })
        
        return all_chunks

    def _extract_citations(self, text: str) -> List[str]:
        """Extract citation patterns from text"""
        citations = []
        
        # Pattern 1: [1], [2], etc.
        numeric_citations = re.findall(r'\[(\d+)\]', text)
        citations.extend([f"[{c}]" for c in numeric_citations])
        
        # Pattern 2: (Author, Year)
        author_year = re.findall(r'\(([A-Z][a-z]+(?:\s+et\s+al\.?)?,\s+\d{4})\)', text)
        citations.extend(author_year)
        
        return list(set(citations))  # Remove duplicates
