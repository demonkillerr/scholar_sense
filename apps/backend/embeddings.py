#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Embeddings Module
Generates embeddings using sentence transformers (BGE-large-en)
"""

import os
import logging
from typing import List, Union
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates embeddings using sentence transformers"""
    
    def __init__(self, model_name: str = "BAAI/bge-large-en-v1.5"):
        """
        Initialize embedding generator
        
        Parameters:
            model_name: Name of the sentence transformer model to use
                       Default: BGE-large-en-v1.5 (best for retrieval)
        """
        self.model_name = model_name
        logger.info(f"Loading embedding model: {model_name}")
        
        try:
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded successfully. Embedding dimension: {self.embedding_dim}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    
    def encode_text(self, text: Union[str, List[str]], batch_size: int = 32) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for text or list of texts
        
        Parameters:
            text: Single text string or list of text strings
            batch_size: Batch size for processing multiple texts
        
        Returns:
            Embedding vector(s) as list or list of lists
        """
        try:
            # Handle single text
            if isinstance(text, str):
                embedding = self.model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            
            # Handle list of texts
            elif isinstance(text, list):
                embeddings = self.model.encode(
                    text,
                    batch_size=batch_size,
                    show_progress_bar=len(text) > 100,
                    convert_to_numpy=True
                )
                return embeddings.tolist()
            
            else:
                raise ValueError(f"Input must be string or list of strings, got {type(text)}")
        
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def encode_query(self, query: str) -> List[float]:
        """
        Generate embedding for a query (adds instruction prefix for BGE models)
        
        Parameters:
            query: Query text
        
        Returns:
            Query embedding vector
        """
        try:
            # BGE models perform better with instruction prefix for queries
            if "bge" in self.model_name.lower():
                query = f"Represent this sentence for searching relevant passages: {query}"
            
            embedding = self.model.encode(query, convert_to_numpy=True)
            return embedding.tolist()
        
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model
        
        Returns:
            Embedding dimension
        """
        return self.embedding_dim


# Global embedding generator instance (lazy loaded)
_embedding_generator = None


def get_embedding_generator(model_name: str = "BAAI/bge-large-en-v1.5") -> EmbeddingGenerator:
    """
    Get or create global embedding generator instance
    
    Parameters:
        model_name: Name of the model to use
    
    Returns:
        EmbeddingGenerator instance
    """
    global _embedding_generator
    
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator(model_name)
    
    return _embedding_generator
