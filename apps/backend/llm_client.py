#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LLM Client Module
Integrates with Google Gemini API for generating citation-grounded answers
"""

import os
import logging
from typing import List, Dict, Any
import google.generativeai as genai

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for Google Gemini API"""
    
    def __init__(self, api_key: str = None, model_name: str = "gemini-pro"):
        """
        Initialize Gemini LLM client
        
        Parameters:
            api_key: Google API key (if None, reads from GEMINI_API_KEY env var)
            model_name: Name of the Gemini model to use
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables or provided")
        
        self.model_name = model_name
        
        # Configure the API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel(model_name)
        
        logger.info(f"Initialized Gemini LLM client with model: {model_name}")
    
    def generate_answer(
        self,
        query: str,
        contexts: List[Dict[str, Any]],
        temperature: float = 0.3,
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        """
        Generate citation-grounded answer from query and retrieved contexts
        
        Parameters:
            query: User's question
            contexts: List of retrieved context chunks with metadata
            temperature: Sampling temperature (0-1, lower = more deterministic)
            max_tokens: Maximum tokens in response
        
        Returns:
            Dictionary with answer, citations, and metadata
        """
        try:
            # Build context string with citations
            context_parts = []
            for i, ctx in enumerate(contexts, 1):
                metadata = ctx.get('metadata', {})
                text = ctx.get('text', '')
                
                paper_title = metadata.get('title', 'Unknown')
                section = metadata.get('section', 'Unknown')
                page = metadata.get('page', 'N/A')
                
                context_parts.append(
                    f"[{i}] Source: {paper_title}, Section: {section}, Page: {page}\n{text}\n"
                )
            
            context_str = "\n".join(context_parts)
            
            # Build prompt
            prompt = self._build_rag_prompt(query, context_str)
            
            # Generate response
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            answer = response.text
            
            # Extract citations from answer
            citations = self._extract_citations(answer, contexts)
            
            return {
                'answer': answer,
                'citations': citations,
                'model': self.model_name,
                'contexts_used': len(contexts)
            }
        
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                'answer': f"Error generating answer: {str(e)}",
                'citations': [],
                'model': self.model_name,
                'error': str(e)
            }
    
    def _build_rag_prompt(self, query: str, contexts: str) -> str:
        """
        Build prompt for RAG-based question answering
        
        Parameters:
            query: User's question
            contexts: Formatted context strings with citations
        
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an expert academic research assistant. Your task is to answer questions about academic papers based on the provided context.

Instructions:
1. Answer the question using ONLY the information provided in the contexts below
2. If the contexts don't contain enough information to answer fully, state what information is missing
3. Always cite your sources using [number] notation matching the context numbers
4. Be precise and academic in your language
5. If multiple papers discuss the topic, compare and contrast their approaches
6. Highlight any disagreements or different perspectives between papers

Contexts:
{contexts}

Question: {query}

Answer:"""
        
        return prompt
    
    def _extract_citations(self, answer: str, contexts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract citation information from answer
        
        Parameters:
            answer: Generated answer text
            contexts: Original contexts with metadata
        
        Returns:
            List of citations found in the answer
        """
        citations = []
        
        for i, ctx in enumerate(contexts, 1):
            # Check if citation [i] appears in answer
            if f"[{i}]" in answer:
                metadata = ctx.get('metadata', {})
                citations.append({
                    'citation_number': i,
                    'paper_title': metadata.get('title', 'Unknown'),
                    'section': metadata.get('section', 'Unknown'),
                    'page': metadata.get('page', 'N/A'),
                    'paper_id': metadata.get('paper_id', '')
                })
        
        return citations
    
    def generate_comparison(
        self,
        papers_data: List[Dict[str, Any]],
        comparison_aspects: List[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Generate multi-paper comparison
        
        Parameters:
            papers_data: List of paper data with chunks and metadata
            comparison_aspects: Specific aspects to compare (methods, results, etc.)
            temperature: Sampling temperature
        
        Returns:
            Comparison result dictionary
        """
        try:
            if comparison_aspects is None:
                comparison_aspects = ["methodology", "results", "conclusions", "limitations"]
            
            # Build comparison prompt
            papers_summary = []
            for i, paper in enumerate(papers_data, 1):
                title = paper.get('title', f'Paper {i}')
                abstract = paper.get('abstract', 'No abstract available')
                papers_summary.append(f"Paper {i}: {title}\nAbstract: {abstract}\n")
            
            papers_str = "\n".join(papers_summary)
            aspects_str = ", ".join(comparison_aspects)
            
            prompt = f"""You are comparing multiple academic papers. Analyze and compare the following papers across these aspects: {aspects_str}.

Papers:
{papers_str}

Provide a structured comparison highlighting:
1. Similarities in approaches or findings
2. Differences in methodology or conclusions
3. Complementary insights
4. Contradictions or disagreements
5. Overall synthesis

Comparison:"""
            
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=2048,
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return {
                'comparison': response.text,
                'papers_compared': len(papers_data),
                'aspects': comparison_aspects,
                'model': self.model_name
            }
        
        except Exception as e:
            logger.error(f"Error generating comparison: {e}")
            return {
                'comparison': f"Error generating comparison: {str(e)}",
                'error': str(e)
            }
    
    def detect_stance(self, text: str, topic: str = None) -> Dict[str, Any]:
        """
        Detect stance in text (supportive, critical, neutral, uncertain)
        
        Parameters:
            text: Text to analyze
            topic: Optional topic to analyze stance towards
        
        Returns:
            Stance detection result
        """
        try:
            topic_str = f" towards '{topic}'" if topic else ""
            
            prompt = f"""Analyze the stance expressed in the following text{topic_str}.

Classify the stance as one of:
- SUPPORTIVE: Expresses positive view, agreement, or support
- CRITICAL: Expresses negative view, disagreement, or criticism
- NEUTRAL: Presents balanced view without clear position
- UNCERTAIN: Expresses doubt, lack of evidence, or need for more research

Provide:
1. Stance classification
2. Confidence score (0-1)
3. Key phrases that indicate this stance
4. Brief explanation

Text: {text}

Analysis:"""
            
            response = self.model.generate_content(prompt)
            
            # Parse response (simplified - could use more structured parsing)
            result_text = response.text
            
            return {
                'stance_analysis': result_text,
                'text': text[:200] + '...' if len(text) > 200 else text
            }
        
        except Exception as e:
            logger.error(f"Error detecting stance: {e}")
            return {
                'stance_analysis': f"Error: {str(e)}",
                'error': str(e)
            }


# Global LLM client instance (lazy loaded)
_llm_client = None


def get_llm_client(api_key: str = None, model_name: str = "gemini-pro") -> LLMClient:
    """
    Get or create global LLM client instance
    
    Parameters:
        api_key: Google API key
        model_name: Model name
    
    Returns:
        LLMClient instance
    """
    global _llm_client
    
    if _llm_client is None:
        _llm_client = LLMClient(api_key, model_name)
    
    return _llm_client
