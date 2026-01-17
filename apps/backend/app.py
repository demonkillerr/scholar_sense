#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sentiment Analysis Backend API
Flask application providing sentiment analysis services
"""

import os
import json
import logging
import tempfile
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from document_processor import DocumentProcessor
from sentiment_analyzer import SentimentAnalyzer
from text_processor import TextProcessor
from logging_config import setup_logging
import sys

# Setup logging first
logger = setup_logging()

# Get the absolute path of the backend directory
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BACKEND_DIR, 'logs')

try:
    # Create logs directory with full permissions
    os.makedirs(LOG_DIR, mode=0o777, exist_ok=True)
    print(f"Created/verified log directory at: {LOG_DIR}")
except Exception as e:
    print(f"Error creating log directory: {e}", file=sys.stderr)
    # Fallback to /tmp if we can't create in the app directory
    LOG_DIR = '/tmp/sentiment_logs'
    os.makedirs(LOG_DIR, mode=0o777, exist_ok=True)
    print(f"Using fallback log directory at: {LOG_DIR}")

LOG_FILE = os.path.join(LOG_DIR, 'app.log')

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure upload settings
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'text', 'json'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure app
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize processors
document_processor = DocumentProcessor()
sentiment_analyzer = SentimentAnalyzer()
text_processor = TextProcessor()

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/status', methods=['GET'])
def status():
    """API endpoint to check service status"""
    try:
        # Check services
        services = document_processor.check_services()
        
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'services': services
        })
    except Exception as e:
        logger.error(f"Error checking status: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/analyse', methods=['POST'])
def analyze_text():
    """API endpoint to analyze text sentiment or process files"""
    try:
        # Get request data
        data = request.get_json()
        logger.info(f"Received data: {data}")
        
        if not data:
            return jsonify({
                'status': 'error',
                'error': 'No data provided'
            }), 400
        
        # Check if topic and file_path are provided
        if 'topic' in data and 'file_path' in data:
            topic = data.get('topic')
            file_path = data.get('file_path')
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
            
            # Check if file exists
            if not os.path.exists(full_path):
                return jsonify({
                    'status': 'error',
                    'error': f'File not found: {file_path}'
                }), 404
            
            # Process file with topic
            result = document_processor.process_file_with_topic(full_path, topic)
            
            return jsonify({
                'status': 'ok',
                'result': result
            })
        
        # Check if topic is provided
        elif 'topic' in data:
            topic = data.get('topic')
            logger.info(f"Analyzing sentiment for topic: {topic}")
            
            # Search for topic-related content in our database or generate sample text
            topic_text = text_processor.generate_topic_text(topic)
            
            if not topic_text:
                return jsonify({
                    'status': 'error',
                    'error': f'Could not generate content for topic: {topic}'
                }), 404
            
            # Analyze sentiment for the topic-related text
            sentiment_result = sentiment_analyzer.analyze_text(topic_text)
            
            # Extract keywords from the topic text
            keywords = text_processor.extract_keywords(topic_text)
            
            return jsonify({
                'status': 'ok',
                'result': {
                    'topic': topic,
                    'sentiment': sentiment_result,
                    'keywords': [{"word": word, "count": count} for word, count in keywords],
                    'sample_text': topic_text[:200] + '...' if len(topic_text) > 200 else topic_text
                }
            })
        
        # Check if file_path is provided
        elif 'file_path' in data:
            file_path = data.get('file_path')
            # Construct full path
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
            
            # Check if file exists
            if not os.path.exists(full_path):
                return jsonify({
                    'status': 'error',
                    'error': f'File not found: {file_path}'
                }), 404
                
            # Process file
            result = document_processor.process_file(full_path)
            
            return jsonify({
                'status': 'ok',
                'result': result
            })
        
        # Check if text is provided
        elif 'text' in data:
            text = data.get('text', '')
            title = data.get('title')
            method = data.get('method', 'combined')
            
            if not text:
                return jsonify({
                    'status': 'error',
                    'error': 'Empty text provided'
                }), 400
            
            # Process text
            if data.get('full_analysis', False):
                # Full document analysis
                result = document_processor.process_text(text, title)
            else:
                # Simple sentiment analysis
                result = sentiment_analyzer.analyze_text(text, method)
            
            return jsonify({
                'status': 'ok',
                'result': result
            })
        
        else:
            return jsonify({
                'status': 'error',
                'error': 'Either topic, text, or file_path must be provided'
            }), 400
    
    except Exception as e:
        logger.error(f"Error analyzing content: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """API endpoint to upload and analyze a file"""
    try:
        # Check if file part exists
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'error': 'No file part in the request'
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'error': 'No file selected'
            }), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename_with_timestamp = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename_with_timestamp)
        
        file.save(file_path)
        logger.info(f"File saved: {file_path}")
        
        # Process file
        result = document_processor.process_file(file_path)
        
        # Add file info to result
        result['file_info'] = {
            'original_filename': filename,
            'saved_filename': filename_with_timestamp,
            'timestamp': timestamp
        }
        
        return jsonify({
            'status': 'ok',
            'result': result
        })
    
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/files/<filename>', methods=['GET'])
def get_file(filename):
    """API endpoint to retrieve an uploaded file"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        logger.error(f"Error retrieving file: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 404

@app.route('/analyze_topic', methods=['POST'])
def analyze_topic():
    """API endpoint to analyze topic of text"""
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'status': 'error',
                'error': 'No text provided'
            }), 400
        
        text = data.get('text', '')
        top_n = data.get('top_n', 10)
        
        if not text:
            return jsonify({
                'status': 'error',
                'error': 'Empty text provided'
            }), 400
        
        # Extract keywords
        keywords = text_processor.extract_keywords(text, top_n=top_n)
        
        # Analyze text structure
        structure = text_processor.analyze_text_structure(text)
        
        # Create summary
        summary = text_processor.summarize_text(text, num_sentences=3)
        
        return jsonify({
            'status': 'ok',
            'result': {
                'keywords': [{'word': word, 'count': count} for word, count in keywords],
                'structure': structure,
                'summary': summary
            }
        })
    
    except Exception as e:
        logger.error(f"Error analyzing topic: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'status': 'error',
        'error': 'File too large'
    }), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 error"""
    return jsonify({
        'status': 'error',
        'error': 'Resource not found'
    }), 404

@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 error"""
    return jsonify({
        'status': 'error',
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Get debug mode from environment or use default
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Start server
    logger.info(f"Starting server on port {port}, debug={debug}")
    app.run(host='0.0.0.0', port=port, debug=debug)