#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GROBID Client Module
For interacting with GROBID service to extract text content from PDF documents
"""

import os
import requests
import logging
import xml.etree.ElementTree as ET
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GrobidClient:
    """GROBID API Client"""

    def __init__(self, base_url=None):
        """
        Initialize GROBID client
        
        Parameters:
            base_url: Base URL of the GROBID service, if None will use environment variable
        """
        # Get base URL from environment variable or use provided value or default
        self.base_url = base_url or os.environ.get("GROBID_URL", "http://localhost:8070")
        logger.warning(f"Using GROBID URL: {self.base_url}")
        self.check_service()
    
    def check_service(self):
        """Check if GROBID service is available"""
        try:
            response = requests.get(f"{self.base_url}/api/version", timeout=5)
            if response.status_code == 200:
                logger.info(f"GROBID service available, version: {response.text}")
                return True
            else:
                logger.warning(f"GROBID service returned error: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Unable to connect to GROBID service: {self.base_url}, error: {e}")
            return False

    def process_fulltext(self, pdf_path):
        """
        Process full text of PDF document
        
        Parameters:
            pdf_path: Path to PDF file
        
        Returns:
            Extracted text content dictionary, including title, abstract, body text, etc.
        """
        logger.info(f"Processing document full text: {pdf_path}")
        url = f"{self.base_url}/api/processFulltextDocument"
        
        try:
            with open(pdf_path, 'rb') as pdf_file:
                files = {'input': (os.path.basename(pdf_path), pdf_file, 'application/pdf')}
                response = requests.post(url, files=files, timeout=120)
            
            if response.status_code != 200:
                logger.error(f"Processing failed: {response.status_code}")
                return None
            
            # Parse XML response
            return self._parse_tei_response(response.text)
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return None
    
    def _parse_tei_response(self, tei_content):
        """
        Parse TEI XML response
        
        Parameters:
            tei_content: TEI XML content
        
        Returns:
            Parsed text content dictionary with sections
        """
        try:
            # Register TEI namespace
            ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
            
            # Parse XML
            root = ET.fromstring(tei_content)
            
            # Extract title
            title_elem = root.find('.//tei:titleStmt/tei:title', ns)
            title = title_elem.text if title_elem is not None else ""
            
            # Extract authors
            author_elems = root.findall('.//tei:fileDesc/tei:sourceDesc//tei:author/tei:persName', ns)
            authors = []
            for author in author_elems:
                forename = author.find('.//tei:forename', ns)
                surname = author.find('.//tei:surname', ns)
                name_parts = []
                if forename is not None and forename.text:
                    name_parts.append(forename.text)
                if surname is not None and surname.text:
                    name_parts.append(surname.text)
                if name_parts:
                    authors.append(' '.join(name_parts))
            authors_str = ', '.join(authors) if authors else ''
            
            # Extract abstract
            abstract_elems = root.findall('.//tei:profileDesc/tei:abstract//tei:p', ns)
            abstract = ' '.join([self._get_element_text(elem) for elem in abstract_elems if elem is not None])
            
            # Extract sections from body
            sections = []
            body = root.find('.//tei:body', ns)
            if body is not None:
                divs = body.findall('.//tei:div', ns)
                for div in divs:
                    # Get section heading
                    head_elem = div.find('.//tei:head', ns)
                    heading = self._get_element_text(head_elem) if head_elem is not None else 'Body'
                    
                    # Get all paragraphs in this section
                    p_elems = div.findall('.//tei:p', ns)
                    section_text = ' '.join([self._get_element_text(p) for p in p_elems if p is not None])
                    
                    if section_text:
                        sections.append({
                            'heading': heading,
                            'text': section_text,
                            'page': 'N/A'  # GROBID doesn't always provide page numbers
                        })
            
            # If no sections found, use all body text as one section
            if not sections:
                body_elems = root.findall('.//tei:body//tei:p', ns)
                body_text = ' '.join([self._get_element_text(elem) for elem in body_elems if elem is not None])
                if body_text:
                    sections.append({
                        'heading': 'Body',
                        'text': body_text,
                        'page': 'N/A'
                    })
            
            # Extract references
            ref_elems = root.findall('.//tei:listBibl/tei:biblStruct', ns)
            references = []
            for ref in ref_elems:
                ref_title = ref.find('.//tei:title', ns)
                if ref_title is not None and ref_title.text:
                    references.append(ref_title.text)
            
            return {
                'title': title,
                'authors': authors_str,
                'abstract': abstract,
                'sections': sections,
                'references': references,
                'body_text': ' '.join([s['text'] for s in sections]),  # Keep for backward compatibility
                'full_text': f"{title} {abstract} {' '.join([s['text'] for s in sections])}"
            }
            
        except Exception as e:
            logger.error(f"Error parsing TEI response: {e}")
            return {
                'title': "",
                'authors': "",
                'abstract': "",
                'sections': [],
                'body_text': "",
                'references': [],
                'full_text': ""
            }
    
    def _get_element_text(self, element):
        """
        Extract all text from an element and its children
        
        Parameters:
            element: XML element
        
        Returns:
            Combined text content
        """
        if element is None:
            return ""
        
        text_parts = []
        if element.text:
            text_parts.append(element.text)
        
        for child in element:
            child_text = self._get_element_text(child)
            if child_text:
                text_parts.append(child_text)
            if child.tail:
                text_parts.append(child.tail)
        
        return ' '.join(text_parts)

# Test code
if __name__ == "__main__":
    client = GrobidClient()
    if client.check_service():
        print("GROBID service available")
    else:
        print("GROBID service not available") 