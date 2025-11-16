#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG Engine Module
Orchestrates the RAG pipeline: chunking, embedding, storage, retrieval, and answer generation
"""

import os
import logging
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime

from vector_store import VectorStore
from embeddings import get_embedding_generator
from llm_client import get_llm_client

logger = logging.getLogger(__name__)


class RAGEngine:
    """Main RAG pipeline orchestrator"""
    
    def __init__(
        self,
        vector_store_path: str = "./chroma_db",
        embedding_model: str = "BAAI/bge-large-en-v1.5",
        llm_api_key: str = None
    ):
        """
        Initialize RAG engine
        
        Parameters:
            vector_store_path: Path to ChromaDB storage
            embedding_model: Name of embedding model to use
            llm_api_key: Gemini API key
        """
        self.vector_store = VectorStore(persist_directory=vector_store_path)
        self.embedding_generator = get_embedding_generator(model_name=embedding_model)
        self.llm_client = get_llm_client(api_key=llm_api_key)
        
        logger.info("RAG Engine initialized successfully")
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        section_name: str = None
    ) -> List[str]:
        """
        Split text into chunks with overlap
        
        Parameters:
            text: Text to chunk
            chunk_size: Target size of each chunk (in characters)
            chunk_overlap: Overlap between chunks
            section_name: Optional section name for context-aware chunking
        
        Returns:
            List of text chunks
        """
        if not text or len(text.strip()) == 0:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            
            # If we're not at the end, try to break at sentence boundary
            if end < text_length:
                # Look for sentence endings (., !, ?) within next 100 chars
                search_end = min(end + 100, text_length)
                sentence_ends = [
                    text.rfind('. ', start, search_end),
                    text.rfind('! ', start, search_end),
                    text.rfind('? ', start, search_end),
                    text.rfind('.\n', start, search_end)
                ]
                
                best_end = max([e for e in sentence_ends if e > start], default=end)
                if best_end > start:
                    end = best_end + 1
            
            chunk = text[start:end].strip()
            
            if chunk:
                # Add section context if available
                if section_name:
                    chunk = f"[Section: {section_name}]\n{chunk}"
                
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - chunk_overlap if end < text_length else text_length
        
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks
    
    def ingest_paper(
        self,
        paper_data: Dict[str, Any],
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> Dict[str, Any]:
        """
        Ingest a paper into the RAG system
        
        Parameters:
            paper_data: Dictionary containing paper information
                - paper_id: Unique identifier
                - title: Paper title
                - authors: Authors string
                - year: Publication year
                - sections: List of sections with 'name' and 'text'
                - abstract: Abstract text
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        
        Returns:
            Dictionary with ingestion results
        """
        try:
            paper_id = paper_data.get('paper_id')
            title = paper_data.get('title', 'Unknown')
            authors = paper_data.get('authors', '')
            year = paper_data.get('year', '')
            sections = paper_data.get('sections', [])
            
            if not paper_id:
                raise ValueError("paper_id is required")
            
            logger.info(f"Ingesting paper: {title}")
            
            all_chunks = []
            all_embeddings = []
            all_metadatas = []
            all_ids = []
            
            # Process each section
            for section in sections:
                section_name = section.get('name', 'Unknown')
                section_text = section.get('text', '')
                page = section.get('page', 'N/A')
                
                if not section_text.strip():
                    continue
                
                # Chunk section text
                chunks = self.chunk_text(
                    section_text,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    section_name=section_name
                )
                
                for i, chunk in enumerate(chunks):
                    # Generate unique ID for chunk
                    chunk_id = self._generate_chunk_id(paper_id, section_name, i)
                    
                    all_chunks.append(chunk)
                    all_ids.append(chunk_id)
                    all_metadatas.append({
                        'paper_id': paper_id,
                        'title': title,
                        'authors': authors,
                        'year': year,
                        'section': section_name,
                        'page': str(page),
                        'chunk_index': i,
                        'upload_date': datetime.now().isoformat()
                    })
            
            if not all_chunks:
                return {
                    'success': False,
                    'error': 'No valid text chunks extracted from paper',
                    'chunks_processed': 0
                }
            
            # Generate embeddings for all chunks
            logger.info(f"Generating embeddings for {len(all_chunks)} chunks...")
            all_embeddings = self.embedding_generator.encode_text(all_chunks)
            
            # Store in vector database
            success = self.vector_store.add_documents(
                documents=all_chunks,
                embeddings=all_embeddings,
                metadatas=all_metadatas,
                ids=all_ids
            )
            
            if success:
                return {
                    'success': True,
                    'paper_id': paper_id,
                    'title': title,
                    'chunks_processed': len(all_chunks),
                    'sections_processed': len(sections)
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to store chunks in vector database',
                    'chunks_processed': 0
                }
        
        except Exception as e:
            logger.error(f"Error ingesting paper: {e}")
            return {
                'success': False,
                'error': str(e),
                'chunks_processed': 0
            }
    
    def query(
        self,
        query: str,
        n_results: int = 5,
        paper_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Query the RAG system and get an answer
        
        Parameters:
            query: User's question
            n_results: Number of context chunks to retrieve
            paper_ids: Optional list of specific paper IDs to search within
        
        Returns:
            Dictionary with answer, citations, and retrieved contexts
        """
        try:
            logger.info(f"Processing query: {query}")
            
            # Generate query embedding
            query_embedding = self.embedding_generator.encode_query(query)
            
            # Build filter if paper_ids specified
            where_filter = None
            if paper_ids:
                # ChromaDB filter syntax
                if len(paper_ids) == 1:
                    where_filter = {"paper_id": paper_ids[0]}
                else:
                    where_filter = {"paper_id": {"$in": paper_ids}}
            
            # Retrieve relevant chunks
            results = self.vector_store.query(
                query_embedding=query_embedding,
                n_results=n_results,
                where=where_filter
            )
            
            if not results['documents']:
                return {
                    'answer': 'No relevant information found in the uploaded papers.',
                    'citations': [],
                    'contexts': []
                }
            
            # Prepare contexts for LLM
            contexts = []
            for doc, metadata, distance in zip(
                results['documents'],
                results['metadatas'],
                results['distances']
            ):
                contexts.append({
                    'text': doc,
                    'metadata': metadata,
                    'relevance_score': 1 - distance  # Convert distance to similarity
                })
            
            # Generate answer using LLM
            llm_response = self.llm_client.generate_answer(
                query=query,
                contexts=contexts
            )
            
            return {
                'answer': llm_response['answer'],
                'citations': llm_response['citations'],
                'contexts': contexts,
                'model': llm_response.get('model', 'unknown'),
                'contexts_used': len(contexts)
            }
        
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'answer': f'Error processing query: {str(e)}',
                'citations': [],
                'contexts': [],
                'error': str(e)
            }
    
    def compare_papers(
        self,
        paper_ids: List[str],
        comparison_aspects: List[str] = None
    ) -> Dict[str, Any]:
        """
        Compare multiple papers
        
        Parameters:
            paper_ids: List of paper IDs to compare
            comparison_aspects: Specific aspects to compare
        
        Returns:
            Comparison result dictionary
        """
        try:
            logger.info(f"Comparing {len(paper_ids)} papers")
            
            papers_data = []
            
            for paper_id in paper_ids:
                # Get paper chunks
                chunks_data = self.vector_store.get_paper_chunks(paper_id)
                
                if not chunks_data['documents']:
                    continue
                
                # Extract title and abstract from metadata
                first_metadata = chunks_data['metadatas'][0] if chunks_data['metadatas'] else {}
                
                # Find abstract in chunks
                abstract = ""
                for doc, meta in zip(chunks_data['documents'], chunks_data['metadatas']):
                    if meta.get('section', '').lower() == 'abstract':
                        abstract = doc
                        break
                
                papers_data.append({
                    'paper_id': paper_id,
                    'title': first_metadata.get('title', 'Unknown'),
                    'authors': first_metadata.get('authors', ''),
                    'year': first_metadata.get('year', ''),
                    'abstract': abstract or 'No abstract available',
                    'sections': len(set(m.get('section') for m in chunks_data['metadatas']))
                })
            
            if len(papers_data) < 2:
                return {
                    'comparison': 'Not enough papers found for comparison',
                    'papers_compared': len(papers_data),
                    'error': 'Need at least 2 papers'
                }
            
            # Generate comparison using LLM
            comparison_result = self.llm_client.generate_comparison(
                papers_data=papers_data,
                comparison_aspects=comparison_aspects
            )
            
            comparison_result['papers'] = papers_data
            
            return comparison_result
        
        except Exception as e:
            logger.error(f"Error comparing papers: {e}")
            return {
                'comparison': f'Error comparing papers: {str(e)}',
                'error': str(e)
            }
    
    def list_papers(self) -> List[Dict[str, Any]]:
        """
        List all papers in the system
        
        Returns:
            List of papers with metadata
        """
        return self.vector_store.list_papers()
    
    def delete_paper(self, paper_id: str) -> bool:
        """
        Delete a paper from the system
        
        Parameters:
            paper_id: Paper ID to delete
        
        Returns:
            True if successful
        """
        return self.vector_store.delete_paper(paper_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get RAG system statistics
        
        Returns:
            Statistics dictionary
        """
        papers = self.list_papers()
        total_chunks = self.vector_store.count_documents()
        
        return {
            'total_papers': len(papers),
            'total_chunks': total_chunks,
            'embedding_model': self.embedding_generator.model_name,
            'embedding_dimension': self.embedding_generator.get_embedding_dimension(),
            'llm_model': self.llm_client.model_name
        }
    
    def _generate_chunk_id(self, paper_id: str, section: str, chunk_index: int) -> str:
        """
        Generate unique chunk ID
        
        Parameters:
            paper_id: Paper identifier
            section: Section name
            chunk_index: Index of chunk within section
        
        Returns:
            Unique chunk ID
        """
        content = f"{paper_id}_{section}_{chunk_index}"
        return hashlib.md5(content.encode()).hexdigest()
