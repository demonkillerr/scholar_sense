#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script: Test only the file upload functionality
"""

import requests
import json
import sys
import os
import unittest

# API endpoint
BASE_URL = "http://localhost:5000"

def test_upload_file(file_path):
    """
    Test uploading a file using the /upload endpoint
    
    Parameters:
        file_path: Path to the file to upload
    
    Returns:
        The JSON result of the upload response
    """
    print(f"Uploading file: {file_path}")
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    if response.status_code != 200:
        print(f"Error uploading file: {response.status_code}")
        print(response.text)
        return None
    
    upload_result = response.json()
    print(f"Upload response: {json.dumps(upload_result, indent=2)}")
    
    if 'result' not in upload_result or 'file_info' not in upload_result['result']:
        print("Error: Invalid upload response format")
        return None
    
    # Get the saved filename
    saved_filename = upload_result['result']['file_info']['saved_filename']
    print(f"Saved filename: {saved_filename}")
    
    return upload_result

class TestUpload(unittest.TestCase):
    """Unit test class for upload functionality"""
    
    def test_valid_file_upload(self):
        """Test uploading a valid file"""
        # Use the specified test file
        test_file = "test/testSample.pdf"
        
        # Check if the test file exists
        if not os.path.exists(test_file):
            self.skipTest(f"Test file not found: {test_file}")
        
        result = test_upload_file(test_file)
        self.assertIsNotNone(result)
        self.assertIn('result', result)
        self.assertIn('file_info', result['result'])
        self.assertIn('saved_filename', result['result']['file_info'])
    
    def test_nonexistent_file(self):
        """Test uploading a nonexistent file"""
        with self.assertRaises(FileNotFoundError):
            test_upload_file("nonexistent_file.txt")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If command line argument is provided, test that file directly
        file_path = sys.argv[1]
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            sys.exit(1)
        
        test_upload_file(file_path)
    else:
        # Default to using the specified test file
        default_test_file = "test/testSample.pdf"
        if os.path.exists(default_test_file):
            test_upload_file(default_test_file)
        else:
            print(f"Error: Default test file not found: {default_test_file}")
            print("Running unit tests instead...")
            unittest.main() 