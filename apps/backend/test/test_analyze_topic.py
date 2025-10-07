#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for the /analyse endpoint with topic parameter
"""

import requests
import json
import sys
import os
import unittest
import glob
import time

# API endpoint
BASE_URL = "http://localhost:5000"

def get_latest_uploaded_file():
    """
    Get the latest file from the uploads directory
    
    Returns:
        The filename of the latest uploaded file
    """
    # Path to uploads directory
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
    
    # Check if uploads directory exists
    if not os.path.exists(upload_dir):
        print(f"Error: Uploads directory not found: {upload_dir}")
        return None
    
    # Get list of files in uploads directory
    files = glob.glob(os.path.join(upload_dir, '*'))
    
    # Check if there are any files
    if not files:
        print("Error: No files found in uploads directory")
        return None
    
    # Get the latest file based on modification time
    latest_file = max(files, key=os.path.getmtime)
    
    # Get just the filename (not the full path)
    filename = os.path.basename(latest_file)
    
    return filename

def test_analyse_topic(topic, latest_file=None):
    """
    Test analyzing sentiment for a specific topic using the /analyse endpoint
    
    Parameters:
        topic: The topic to analyze
        latest_file: Optional filename to analyze
    
    Returns:
        The JSON result of the analysis
    """
    print(f"Analyzing sentiment for topic: {topic}")
    
    # Prepare payload
    payload = {
        "topic": topic
    }
    
    # Add file_path if provided
    if latest_file:
        payload["file_path"] = latest_file
        print(f"Using file: {latest_file}")
    
    # Call the analyse endpoint
    try:
        response = requests.post(f"{BASE_URL}/analyse", json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to API: {e}")
        return {"status": "error", "error": f"Connection error: {str(e)}"}
    
    try:
        result = response.json()
    except json.JSONDecodeError:
        print(f"Error decoding JSON response: {response.text}")
        return {"status": "error", "error": "Invalid JSON response"}
    
    print(f"Analysis response status: {result.get('status')}")
    
    return result

class TestAnalyseTopic(unittest.TestCase):
    """Unit test class for analyse functionality with topics"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class - get the latest uploaded file"""
        cls.latest_file = get_latest_uploaded_file()
        
        # Create test directory and file if it doesn't exist
        test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data')
        os.makedirs(test_data_dir, exist_ok=True)
        
        # Get test article path
        cls.test_article_path = os.path.join(test_data_dir, 'sample_article.txt')
        
        # Verify API is accessible before running tests
        try:
            response = requests.get(f"{BASE_URL}/status")
            if response.status_code != 200:
                print(f"Warning: API status check failed with code {response.status_code}")
                print(f"Response: {response.text}")
            else:
                print("API status check passed")
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not connect to API: {e}")
    
    def test_analyse_human_beings_topic(self):
        """Test analyzing 'human beings' topic sentiment"""
        topic = "human beings"
        result = test_analyse_topic(topic, self.latest_file)
        
        self.assertIsNotNone(result)
        
        # Debug output
        print(f"\nFull response for {topic}:")
        print(json.dumps(result, indent=2))
        
        # Check if the result contains error information
        if result.get('status') == 'error':
            self.fail(f"API returned error: {result.get('error', 'Unknown error')}")
            
        self.assertEqual(result.get('status'), 'ok')
        self.assertIn('result', result)
        
        # Print result information
        if 'result' in result:
            result_data = result['result']
            
            # Print topic
            print(f"\nTopic: {result_data.get('topic')}")
            
            # Print sentiment if available
            if 'sentiment' in result_data:
                sentiment = result_data['sentiment']
                print("\nSentiment:")
                
                # Check if sentiment has stance information
                stance = None
                if isinstance(sentiment, dict):
                    if 'stance' in sentiment:
                        stance = sentiment.get('stance')
                        print(f"- Stance: {stance}")
                    
                    if 'sentiment' in sentiment:
                        print(f"- Overall: {sentiment.get('sentiment')} (score: {sentiment.get('score')})")
                    elif 'label' in sentiment:
                        print(f"- Overall: {sentiment.get('label')} (score: {sentiment.get('score')})")
                else:
                    print(f"- Overall: {sentiment}")
                
                # If stance is available, verify it
                if stance is not None:
                    # Use less strict verification - verify stance is positive
                    positive_stances = ['support', 'positive', 'favor', 'pro']
                    stance_match = any(s in stance.lower() for s in positive_stances)
                    self.assertTrue(stance_match, 
                                    f"Expected positive stance for topic '{topic}', got '{stance}'")
                    print(f"✓ Stance verification passed: '{stance}' for '{topic}' (positive stance)")
                else:
                    print("Note: No stance information available in response")
            
            # Print keywords if available
            if 'keywords' in result_data:
                print("\nTop keywords:")
                for keyword in result_data['keywords'][:5]:  # Print top 5 keywords
                    print(f"- {keyword['word']} ({keyword['count']})")
            
            # Print sample text if available
            if 'sample_text' in result_data:
                print(f"\nSample Text: {result_data['sample_text'][:100]}...")
    
    def test_analyse_ai_topic(self):
        """Test analyzing 'AI' topic sentiment"""
        topic = "AI"
        result = test_analyse_topic(topic, self.latest_file)
        
        self.assertIsNotNone(result)
        
        # Debug output
        print(f"\nFull response for {topic}:")
        print(json.dumps(result, indent=2))
        
        # Check if the result contains error information
        if result.get('status') == 'error':
            self.fail(f"API returned error: {result.get('error', 'Unknown error')}")
            
        self.assertEqual(result.get('status'), 'ok')
        self.assertIn('result', result)
        
        # Print result information
        if 'result' in result:
            result_data = result['result']
            
            # Print topic
            print(f"\nTopic: {result_data.get('topic')}")
            
            # Print sentiment if available
            if 'sentiment' in result_data:
                sentiment = result_data['sentiment']
                print("\nSentiment:")
                
                # Check if sentiment has stance information
                stance = None
                if isinstance(sentiment, dict):
                    if 'stance' in sentiment:
                        stance = sentiment.get('stance')
                        print(f"- Stance: {stance}")
                    
                    if 'sentiment' in sentiment:
                        print(f"- Overall: {sentiment.get('sentiment')} (score: {sentiment.get('score')})")
                    elif 'label' in sentiment:
                        print(f"- Overall: {sentiment.get('label')} (score: {sentiment.get('score')})")
                else:
                    print(f"- Overall: {sentiment}")
                
                # If stance is available, verify it
                if stance is not None:
                    # Use less strict verification - check for neutral or similar terms
                    neutral_stances = ['neutral', 'balanced', 'objective', 'impartial']
                    stance_match = any(s in stance.lower() for s in neutral_stances)
                    self.assertTrue(stance_match, 
                                   f"Expected neutral stance for topic '{topic}', got '{stance}'")
                    print(f"✓ Stance verification passed: '{stance}' for '{topic}' (neutral stance)")
                else:
                    print("Note: No stance information available in response")
            
            # Print keywords if available
            if 'keywords' in result_data:
                print("\nTop keywords:")
                for keyword in result_data['keywords'][:5]:  # Print top 5 keywords
                    print(f"- {keyword['word']} ({keyword['count']})")
            
            # Print sample text if available
            if 'sample_text' in result_data:
                print(f"\nSample Text: {result_data['sample_text'][:100]}...")
    
    def test_analyse_mpi_topic(self):
        """Test analyzing 'mpi' topic (which should not be associated with the document)"""
        topic = "mpi"
        result = test_analyse_topic(topic, self.latest_file)
        
        self.assertIsNotNone(result)
        
        # Debug output
        print(f"\nFull response for {topic}:")
        print(json.dumps(result, indent=2))
        
        # Check for appropriate error status or message
        expected_message_parts = [
            "not associated with", 
            "cannot be analyzed", 
            "try another"
        ]
        
        # The response format could vary, we'll be more flexible in checking
        message_found = False
        error_message = ""
        
        # Function to recursively search in nested dictionaries
        def search_in_dict(d, parts):
            if not isinstance(d, dict):
                return False, ""
                
            # Check each value in the dictionary
            for key, value in d.items():
                if isinstance(value, str):
                    # Check if all parts are in the string
                    if all(part.lower() in value.lower() for part in parts):
                        return True, value
                elif isinstance(value, dict):
                    # Recursively search in nested dictionary
                    found, msg = search_in_dict(value, parts)
                    if found:
                        return True, msg
            return False, ""
        
        # Try to find message in the response
        message_found, error_message = search_in_dict(result, expected_message_parts)
        
        # Also check if it's explicitly marked as an error
        # It might be a valid response with different phrasing
        error_status = result.get('status') == 'error'
        
        # Output the result for debugging
        print(f"\nResponse for topic '{topic}':")
        
        # Mark the test as successful if either:
        # 1. We found the expected error message parts
        # 2. The API explicitly returned an error status
        self.assertTrue(message_found or error_status, 
                      f"Expected error response for unrelated topic '{topic}' not found in response")
                      
        if message_found:
            print(f"✓ Verification passed: Found error message: '{error_message}'")
        elif error_status:
            print(f"✓ Verification passed: API returned error status")
        else:
            print("✗ Verification failed: No error message or status found")
    
    def test_analyse_with_text_only(self):
        """Test analyzing with only text (no topic)"""
        # Read test article content
        if os.path.exists(self.test_article_path):
            with open(self.test_article_path, 'r') as f:
                content = f.read()
            
            # Call analyze endpoint with just text
            payload = {
                "text": content,
                "full_analysis": True
            }
            
            # Use try-except for API call
            try:
                response = requests.post(f"{BASE_URL}/analyse", json=payload)
                response.raise_for_status()
                result = response.json()
            except requests.exceptions.RequestException as e:
                self.fail(f"Error connecting to API: {e}")
                return
            except json.JSONDecodeError:
                self.fail(f"Error decoding JSON response: {response.text}")
                return
                
            # Debug output
            print("\nFull response for text-only analysis:")
            print(json.dumps(result, indent=2))
            
            self.assertIsNotNone(result)
            self.assertEqual(result.get('status'), 'ok')
            self.assertIn('result', result)
            
            print("\nText-only analysis (no topic):")
            print(f"Status: {result.get('status')}")
            
            # Print basic result info
            if 'result' in result and isinstance(result['result'], dict):
                if 'sentiment' in result['result']:
                    sentiment = result['result']['sentiment']
                    print(f"\nOverall sentiment: {sentiment}")
                
                if 'keywords' in result['result']:
                    print("\nTop keywords:")
                    for keyword in result['result']['keywords'][:5]:
                        print(f"- {keyword['word']} ({keyword['count']})")
        else:
            self.skipTest(f"Test article not found: {self.test_article_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If command line argument is provided, use it as topic
        topic = sys.argv[1]
        latest_file = None
        
        # If two arguments, second is the file path
        if len(sys.argv) > 2:
            latest_file = sys.argv[2]
        else:
            # Try to get latest file
            latest_file = get_latest_uploaded_file()
        
        print(f"Running test with topic: {topic}")
        test_analyse_topic(topic, latest_file)
    else:
        print("Running unit tests")
        unittest.main() 