#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GROBID API Usage Example
This script demonstrates how to use GROBID's REST API to process PDF documents
"""

import os
import sys
import json
import requests
from pathlib import Path


class GrobidClient:
    """GROBID API Client"""

    def __init__(self, base_url="http://localhost:8070"):
        """
        Initialize GROBID client
        
        Parameters:
            base_url: Base URL of the GROBID service
        """
        self.base_url = base_url
        # Check if GROBID service is available
        try:
            response = requests.get(f"{self.base_url}/api/version")
            if response.status_code == 200:
                print(f"GROBID service available, version: {response.text}")
            else:
                print(f"GROBID service returned error: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"Unable to connect to GROBID service: {self.base_url}")
            print("Please make sure the GROBID service is running")
            sys.exit(1)

    def process_header(self, pdf_path, output_path=None):
        """
        Process the header section of a PDF document
        
        Parameters:
            pdf_path: Path to the PDF file
            output_path: Output file path (optional)
        
        Returns:
            Processed TEI XML text
        """
        print(f"Processing document header: {pdf_path}")
        url = f"{self.base_url}/api/processHeaderDocument"
        
        with open(pdf_path, 'rb') as pdf_file:
            files = {'input': (os.path.basename(pdf_path), pdf_file, 'application/pdf')}
            response = requests.post(url, files=files)
        
        if response.status_code != 200:
            print(f"Processing failed: {response.status_code}")
            return None
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as out_file:
                out_file.write(response.text)
            print(f"Header information saved to: {output_path}")
        
        return response.text

    def process_fulltext(self, pdf_path, output_path=None):
        """
        Process the full text of a PDF document
        
        Parameters:
            pdf_path: Path to the PDF file
            output_path: Output file path (optional)
        
        Returns:
            Processed TEI XML text
        """
        print(f"Processing document full text: {pdf_path}")
        url = f"{self.base_url}/api/processFulltextDocument"
        
        with open(pdf_path, 'rb') as pdf_file:
            files = {'input': (os.path.basename(pdf_path), pdf_file, 'application/pdf')}
            response = requests.post(url, files=files)
        
        if response.status_code != 200:
            print(f"Processing failed: {response.status_code}")
            return None
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as out_file:
                out_file.write(response.text)
            print(f"Full text information saved to: {output_path}")
        
        return response.text

    def process_references(self, pdf_path, output_path=None):
        """
        Process references in a PDF document
        
        Parameters:
            pdf_path: Path to the PDF file
            output_path: Output file path (optional)
        
        Returns:
            Processed TEI XML text
        """
        print(f"Processing document references: {pdf_path}")
        url = f"{self.base_url}/api/processReferences"
        
        with open(pdf_path, 'rb') as pdf_file:
            files = {'input': (os.path.basename(pdf_path), pdf_file, 'application/pdf')}
            response = requests.post(url, files=files)
        
        if response.status_code != 200:
            print(f"Processing failed: {response.status_code}")
            return None
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as out_file:
                out_file.write(response.text)
            print(f"References information saved to: {output_path}")
        
        return response.text


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python grobid-api-example.py <pdf_file_path> [grobid_service_URL]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Error: File does not exist: {pdf_path}")
        sys.exit(1)
    
    # Check if file is a PDF
    if not pdf_path.lower().endswith('.pdf'):
        print(f"Warning: File may not be a PDF: {pdf_path}")
    
    # Set GROBID service URL
    grobid_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8070"
    
    # Create output directory
    output_dir = Path("grobid_output")
    output_dir.mkdir(exist_ok=True)
    
    # Get filename (without extension)
    filename = Path(pdf_path).stem
    
    # Initialize GROBID client
    client = GrobidClient(grobid_url)
    
    # Process document header
    header_output = output_dir / f"{filename}_header.xml"
    client.process_header(pdf_path, header_output)
    
    # Process document full text
    fulltext_output = output_dir / f"{filename}_fulltext.xml"
    client.process_fulltext(pdf_path, fulltext_output)
    
    # Process references
    references_output = output_dir / f"{filename}_references.xml"
    client.process_references(pdf_path, references_output)
    
    print("\nProcessing complete! Output files saved in 'grobid_output' directory")


if __name__ == "__main__":
    main() 