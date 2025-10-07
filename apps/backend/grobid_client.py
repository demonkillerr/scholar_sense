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
                response = requests.post(url, files=files, timeout=30)
            
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
            Parsed text content dictionary
        """
        try:
            # Register TEI namespace
            ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
            
            # Parse XML
            root = ET.fromstring(tei_content)
            
            # Extract title
            title_elem = root.find('.//tei:titleStmt/tei:title', ns)
            title = title_elem.text if title_elem is not None else ""
            
            # Extract abstract
            abstract_elems = root.findall('.//tei:profileDesc/tei:abstract//tei:p', ns)
            abstract = ' '.join([elem.text for elem in abstract_elems if elem.text]) if abstract_elems else ""
            
            # Extract body paragraphs
            body_elems = root.findall('.//tei:body//tei:p', ns)
            body_text = ' '.join([elem.text for elem in body_elems if elem.text]) if body_elems else ""
            
            # Extract references
            ref_elems = root.findall('.//tei:listBibl/tei:biblStruct', ns)
            references = []
            for ref in ref_elems:
                ref_title = ref.find('.//tei:title', ns)
                if ref_title is not None and ref_title.text:
                    references.append(ref_title.text)
            
            return {
                'title': title,
                'abstract': abstract,
                'body_text': body_text,
                'references': references,
                'full_text': f"{title} {abstract} {body_text}"
            }
            
        except Exception as e:
            logger.error(f"Error parsing TEI response: {e}")
            return {
                'title': "",
                'abstract': "",
                'body_text': "",
                'references': [],
                'full_text': ""
            }

# Test code
if __name__ == "__main__":
    client = GrobidClient()
    if client.check_service():
        print("GROBID service available")
    else:
        print("GROBID service not available") 