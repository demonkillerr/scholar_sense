#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Document Processing Module
Processes documents using GROBID and extracts structured information for RAG
"""

import os
import json
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from grobid_client import GrobidClient

# Get logger for this module
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Document processing class for extracting and analyzing document content"""
    
    def __init__(self, grobid_url=None):
        """
        Initialize document processor
        
        Parameters:
            grobid_url: URL of the GROBID service, if None will use environment variable
        """
        # Get GROBID URL from environment variable or use provided value or default
        self.grobid_url = grobid_url or os.environ.get("GROBID_URL", "http://localhost:8070")
        logger.info(f"Using GROBID URL: {self.grobid_url}")
        self.grobid_client = GrobidClient(self.grobid_url)
        self.upload_dir = os.environ.get("UPLOAD_DIR", "uploads")
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def check_services(self):
        """
        Check if all required services are available
        
        Returns:
            Dictionary with service status information
        """
        services = {}
        
        # Check GROBID service
        try:
            grobid_status = self.grobid_client.check_service()
            services["grobid"] = {
                "available": grobid_status,
                "url": self.grobid_client.base_url
            }
        except Exception as e:
            logger.error(f"Error checking GROBID service: {e}")
            services["grobid"] = {
                "available": False,
                "error": str(e),
                "url": self.grobid_client.base_url
            }
        
        return services
    
    def process_file_for_rag(self, file_path: str) -> Dict[str, Any]:
        """
        Process a document file for RAG ingestion
        
        Parameters:
            file_path: Path to the document file
        
        Returns:
            Dictionary with structured paper data ready for RAG ingestion
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return {"error": "File not found"}
        
        # Only support PDF files for academic papers
        if file_path.suffix.lower() == '.pdf':
            return self._process_pdf_for_rag(file_path)
        else:
            logger.error(f"Unsupported file type: {file_path.suffix}")
            return {"error": f"Only PDF files are supported for academic papers"}
    
    def _process_pdf_for_rag(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a PDF document using GROBID for RAG ingestion
        
        Parameters:
            file_path: Path to the PDF file
        
        Returns:
            Dictionary with structured paper data ready for RAG
        """
        logger.info(f"Processing PDF file for RAG: {file_path}")
        
        try:
            # Extract text using GROBID
            grobid_result = self.grobid_client.process_fulltext(file_path)
            
            if not grobid_result:
                return {"error": "Failed to process PDF with GROBID"}
            
            # Generate paper ID from filename and timestamp
            paper_id = self._generate_paper_id(file_path.name)
            
            # Extract structured data
            paper_data = {
                'paper_id': paper_id,
                'filename': file_path.name,
                'file_size': file_path.stat().st_size,
                'upload_date': datetime.now().isoformat(),
                'title': grobid_result.get('title', 'Unknown'),
                'authors': grobid_result.get('authors', ''),
                'year': self._extract_year(grobid_result),
                'abstract': grobid_result.get('abstract', ''),
                'sections': self._extract_sections(grobid_result),
                'references': grobid_result.get('references', [])
            }
            
            logger.info(f"Extracted paper: {paper_data['title']}")
            logger.info(f"Found {len(paper_data['sections'])} sections")
            
            return paper_data
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return {"error": f"Error processing PDF: {str(e)}"}
    
    def _generate_paper_id(self, filename: str) -> str:
        """
        Generate unique paper ID from filename and timestamp
        
        Parameters:
            filename: Original filename
        
        Returns:
            Unique paper ID
        """
        timestamp = datetime.now().isoformat()
        content = f"{filename}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _extract_year(self, grobid_result: Dict[str, Any]) -> str:
        """
        Extract publication year from GROBID result
        
        Parameters:
            grobid_result: GROBID processing result
        
        Returns:
            Year string or empty string
        """
        # Try to extract year from various fields
        # Could be in title, metadata, or references
        # This is a simplified version
        return grobid_result.get('year', '')
    
    def _extract_sections(self, grobid_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract sections from GROBID result
        
        Parameters:
            grobid_result: GROBID processing result
        
        Returns:
            List of sections with name, text, and page info
        """
        sections = []
        
        # Add abstract as first section
        if grobid_result.get('abstract'):
            sections.append({
                'name': 'Abstract',
                'text': grobid_result['abstract'],
                'page': 1
            })
        
        # Add body sections
        if grobid_result.get('sections'):
            for section in grobid_result['sections']:
                if section.get('text'):
                    sections.append({
                        'name': section.get('heading', 'Body'),
                        'text': section.get('text', ''),
                        'page': section.get('page', 'N/A')
                    })
        elif grobid_result.get('body_text'):
            # If no sections, use entire body as one section
            sections.append({
                'name': 'Body',
                'text': grobid_result['body_text'],
                'page': 'N/A'
            })
        
        return sections
    
    def _process_text_file(self, file_path):
        """
        Process a text file
        
        Parameters:
            file_path: Path to the text file
        
        Returns:
            Dictionary with extracted document information
        """
        logger.info(f"Processing text file: {file_path}")
        
        try:
            # Read text file
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            # Process text
            document_data = {
                'full_text': text_content
            }
            
            # Try to extract title (first line)
            lines = text_content.strip().split('\n')
            if lines:
                document_data['title'] = lines[0].strip()
                
                # If there are more lines, consider the rest as body
                if len(lines) > 1:
                    document_data['body_text'] = '\n'.join(lines[1:]).strip()
            
            # Analyze document sentiment
            sentiment_result = self.sentiment_analyzer.analyze_document(document_data)
            
            # Extract keywords
            keywords = self.text_processor.extract_keywords(text_content, top_n=10)
            document_data['keywords'] = [{"word": word, "count": count} for word, count in keywords]
            
            # Combine results
            result = {
                "document": document_data,
                "sentiment": sentiment_result,
                "file_info": {
                    "filename": file_path.name,
                    "file_type": "text",
                    "file_size": file_path.stat().st_size
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing text file: {e}")
            return {"error": f"Error processing text file: {str(e)}"}
    
    def _process_json_file(self, file_path):
        """
        Process a JSON file
        
        Parameters:
            file_path: Path to the JSON file
        
        Returns:
            Dictionary with extracted document information
        """
        logger.info(f"Processing JSON file: {file_path}")
        
        try:
            # Read JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Check if JSON has expected structure
            if not isinstance(json_data, dict):
                return {"error": "Invalid JSON format: root must be an object"}
            
            # Extract document data
            document_data = {}
            
            # Extract title
            if json_data.get('title'):
                document_data['title'] = json_data['title']
            
            # Extract abstract
            if json_data.get('abstract'):
                document_data['abstract'] = json_data['abstract']
            
            # Extract body text
            if json_data.get('body_text') or json_data.get('text') or json_data.get('content'):
                document_data['body_text'] = json_data.get('body_text') or json_data.get('text') or json_data.get('content')
            
            # Extract authors
            if json_data.get('authors'):
                document_data['authors'] = json_data['authors']
            
            # Combine all text for full-text analysis
            full_text_parts = []
            if document_data.get('title'):
                full_text_parts.append(document_data['title'])
            if document_data.get('abstract'):
                full_text_parts.append(document_data['abstract'])
            if document_data.get('body_text'):
                full_text_parts.append(document_data['body_text'])
            
            document_data['full_text'] = ' '.join(full_text_parts)
            
            # If no document parts were found, use the entire JSON as full text
            if not document_data.get('full_text'):
                document_data['full_text'] = json.dumps(json_data)
            
            # Analyze document sentiment
            sentiment_result = self.sentiment_analyzer.analyze_document(document_data)
            
            # Extract keywords
            keywords = self.text_processor.extract_keywords(document_data['full_text'], top_n=10)
            document_data['keywords'] = [{"word": word, "count": count} for word, count in keywords]
            
            # Combine results
            result = {
                "document": document_data,
                "sentiment": sentiment_result,
                "file_info": {
                    "filename": file_path.name,
                    "file_type": "json",
                    "file_size": file_path.stat().st_size
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing JSON file: {e}")
            return {"error": f"Error processing JSON file: {str(e)}"}
    
    def process_text(self, text, title=None):
        """
        Process text content directly
        
        Parameters:
            text: Text content to process
            title: Optional title for the text
        
        Returns:
            Dictionary with extracted document information
        """
        logger.info("Processing text content")
        
        try:
            # Create document data
            document_data = {
                'full_text': text
            }
            
            if title:
                document_data['title'] = title
            
            # Extract sentences
            sentences = self.text_processor.extract_sentences(text)
            
            # If no title provided, use first sentence as title
            if not title and sentences:
                document_data['title'] = sentences[0]
                # Use remaining sentences as body text
                if len(sentences) > 1:
                    document_data['body_text'] = ' '.join(sentences[1:])
            else:
                document_data['body_text'] = text
            
            # Analyze document sentiment
            sentiment_result = self.sentiment_analyzer.analyze_document(document_data)
            
            # Extract keywords
            keywords = self.text_processor.extract_keywords(text, top_n=10)
            document_data['keywords'] = [{"word": word, "count": count} for word, count in keywords]
            
            # Combine results
            result = {
                "document": document_data,
                "sentiment": sentiment_result,
                "file_info": {
                    "file_type": "text",
                    "text_length": len(text)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing text content: {e}")
            return {"error": f"Error processing text content: {str(e)}"}
    
    def save_uploaded_file(self, file_data, filename):
        """
        Save uploaded file to disk
        
        Parameters:
            file_data: File data (bytes)
            filename: Name of the file
        
        Returns:
            Path to the saved file
        """
        try:
            # Ensure filename is safe
            safe_filename = os.path.basename(filename)
            file_path = os.path.join(self.upload_dir, safe_filename)
            
            # Write file to disk
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            logger.info(f"File saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise
    
    def process_file_with_topic(self, file_path, topic):
        """
        Process a document file with respect to a specific topic
        
        Parameters:
            file_path: Path to the document file
            topic: Topic to analyze the document against
        
        Returns:
            Dictionary with topic-based analysis results
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return {"error": "File not found"}
        
        try:
            logger.info(f"Processing file with topic: {topic}, file: {file_path}")
            
            # First process the document normally (this will use GROBID for PDF files)
            doc_result = self.process_file(file_path)
            
            if "error" in doc_result:
                logger.error(f"Error in document processing: {doc_result['error']}")
                return doc_result
            
            # Get the full text from the document
            full_text = doc_result["document"].get("full_text", "")
            
            if not full_text:
                logger.warning(f"Empty text extracted from file: {file_path}")
                return {"error": "No text could be extracted from the document"}
            
            logger.info(f"Successfully extracted text from document, length: {len(full_text)} characters")
            
            # Extract topic-related sentences
            topic_sentences = self.text_processor.extract_topic_sentences(full_text, topic)
            logger.info(f"Found {len(topic_sentences)} sentences related to topic '{topic}'")
            
            # If no topic-related sentences found, use the full text
            if not topic_sentences:
                logger.info(f"No sentences related to topic '{topic}' found. Using full text for analysis.")
                topic_sentences = self.text_processor.extract_sentences(full_text)[:10]  # Use first 10 sentences
                logger.info(f"Using first {len(topic_sentences)} sentences from document")
            
            # Analyze sentiment for topic-related content
            topic_text = " ".join(topic_sentences)
            logger.info(f"Analyzing sentiment for topic text, length: {len(topic_text)} characters")
            topic_sentiment = self.sentiment_analyzer.analyze_text(topic_text)
            
            # Calculate topic relevance score
            relevance_score = self.text_processor.calculate_topic_relevance(full_text, topic)
            logger.info(f"Topic relevance score: {relevance_score}")
            
            # Check if relevance score is too low
            if relevance_score < 0.05:
                logger.info(f"Relevance score too low: {relevance_score}, not proceeding with analysis")
                return {
                    "document": doc_result["document"],
                    "topic_analysis": {
                        "topic": topic,
                        "relevance_score": relevance_score,
                        "low_relevance": True,
                        "message": "This topic is not associated with the uploaded document and cannot be analyzed. Please try another related topic"
                    },
                    "file_info": doc_result["file_info"]
                }
            
            # Extract topic-specific keywords
            topic_keywords = self.text_processor.extract_topic_keywords(full_text, topic)
            
            # If no topic-specific keywords found, use general keywords
            if not topic_keywords:
                logger.info(f"No keywords related to topic '{topic}' found. Using general keywords.")
                topic_keywords = self.text_processor.extract_keywords(full_text)
            
            # Determine stance (support/oppose/neutral)
            stance = self._determine_stance(topic_sentiment, relevance_score)
            logger.info(f"Determined stance: {stance}")
            
            # Combine results
            result = {
                "document": doc_result["document"],
                "topic_analysis": {
                    "topic": topic,
                    "stance": stance,
                    "relevance_score": relevance_score,
                    "sentiment": topic_sentiment,
                    "topic_sentences": topic_sentences,
                    "topic_keywords": topic_keywords
                },
                "file_info": doc_result["file_info"]
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing file with topic: {e}")
            return {"error": f"Error processing file with topic: {str(e)}"}
    
    def _determine_stance(self, sentiment_result, relevance_score):
        """
        Determine the stance of the document regarding the topic
        
        Parameters:
            sentiment_result: Sentiment analysis result
            relevance_score: Topic relevance score
        
        Returns:
            String indicating the stance: 'support', 'oppose', or 'neutral'
        """
        if relevance_score < 0.3:  # Low relevance threshold
            return "neutral"
        
        sentiment_score = sentiment_result.get("score", 0)
        
        if sentiment_score > 0.2:  # Positive sentiment threshold
            return "support"
        elif sentiment_score < -0.2:  # Negative sentiment threshold
            return "oppose"
        else:
            return "neutral"

# Test code
if __name__ == "__main__":
    processor = DocumentProcessor()
    
    # Check services
    services = processor.check_services()
    print("Services status:", services)
    
    # Test with a sample text
    test_text = """
    Natural language processing (NLP) is a subfield of linguistics, computer science, and artificial intelligence 
    concerned with the interactions between computers and human language, in particular how to program computers 
    to process and analyze large amounts of natural language data. The goal is a computer capable of "understanding" 
    the contents of documents, including the contextual nuances of the language within them.
    """
    
    result = processor.process_text(test_text, title="Introduction to NLP")
    print(json.dumps(result, indent=2)) 