#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vector Store Module
Manages ChromaDB for storing and retrieving document embeddings
"""

import os
import logging
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages vector database operations using ChromaDB"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize ChromaDB vector store
        
        Parameters:
            persist_directory: Directory to persist the vector database
        """
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection_name = "academic_papers"
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Loaded existing collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Academic paper chunks with embeddings"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
    
    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> bool:
        """
        Add documents with embeddings to the vector store
        
        Parameters:
            documents: List of document text chunks
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            ids: List of unique IDs for each chunk
        
        Returns:
            True if successful
        """
        try:
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to vector store")
            return True
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            return False
    
    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query the vector store for similar documents
        
        Parameters:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Optional metadata filter
        
        Returns:
            Dictionary with query results including documents, metadatas, distances
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )
            
            logger.info(f"Query returned {len(results['documents'][0])} results")
            return {
                'documents': results['documents'][0],
                'metadatas': results['metadatas'][0],
                'distances': results['distances'][0],
                'ids': results['ids'][0]
            }
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            return {
                'documents': [],
                'metadatas': [],
                'distances': [],
                'ids': []
            }
    
    def get_paper_chunks(self, paper_id: str) -> Dict[str, Any]:
        """
        Get all chunks for a specific paper
        
        Parameters:
            paper_id: Paper ID to retrieve chunks for
        
        Returns:
            Dictionary with all chunks and metadata for the paper
        """
        try:
            results = self.collection.get(
                where={"paper_id": paper_id}
            )
            logger.info(f"Retrieved {len(results['documents'])} chunks for paper {paper_id}")
            return results
        except Exception as e:
            logger.error(f"Error retrieving paper chunks: {e}")
            return {'documents': [], 'metadatas': [], 'ids': []}
    
    def list_papers(self) -> List[Dict[str, Any]]:
        """
        List all papers in the vector store
        
        Returns:
            List of unique papers with their metadata
        """
        try:
            # Get all documents
            all_docs = self.collection.get()
            
            # Extract unique papers
            papers = {}
            for metadata in all_docs['metadatas']:
                paper_id = metadata.get('paper_id')
                if paper_id and paper_id not in papers:
                    papers[paper_id] = {
                        'paper_id': paper_id,
                        'title': metadata.get('title', 'Unknown'),
                        'authors': metadata.get('authors', ''),
                        'year': metadata.get('year', ''),
                        'upload_date': metadata.get('upload_date', '')
                    }
            
            return list(papers.values())
        except Exception as e:
            logger.error(f"Error listing papers: {e}")
            return []
    
    def delete_paper(self, paper_id: str) -> bool:
        """
        Delete all chunks for a specific paper
        
        Parameters:
            paper_id: Paper ID to delete
        
        Returns:
            True if successful
        """
        try:
            # Get all chunk IDs for this paper
            results = self.collection.get(where={"paper_id": paper_id})
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} chunks for paper {paper_id}")
                return True
            else:
                logger.warning(f"No chunks found for paper {paper_id}")
                return False
        except Exception as e:
            logger.error(f"Error deleting paper: {e}")
            return False
    
    def count_documents(self) -> int:
        """
        Count total documents in the vector store
        
        Returns:
            Number of documents
        """
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            return 0
    
    def reset(self) -> bool:
        """
        Reset the entire vector store (use with caution!)
        
        Returns:
            True if successful
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Academic paper chunks with embeddings"}
            )
            logger.warning("Vector store has been reset!")
            return True
        except Exception as e:
            logger.error(f"Error resetting vector store: {e}")
            return False
