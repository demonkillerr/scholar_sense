#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ScholarSense Backend API
Flask application providing RAG-powered academic paper Q&A
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from document_processor import DocumentProcessor
from rag_engine import RAGEngine
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
ALLOWED_EXTENSIONS = {'pdf'}  # Only PDF for academic papers
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB for academic papers

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure app
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize processors
document_processor = DocumentProcessor()

# Initialize RAG engine (lazy loaded)
_rag_engine = None

def get_rag_engine():
    """Get or create RAG engine instance"""
    global _rag_engine
    if _rag_engine is None:
        try:
            logger.info("Initializing RAG engine...")
            _rag_engine = RAGEngine(
                vector_store_path=os.environ.get('VECTOR_STORE_PATH', './chroma_db'),
                embedding_model=os.environ.get('EMBEDDING_MODEL', 'BAAI/bge-large-en-v1.5'),
                llm_api_key=os.environ.get('GEMINI_API_KEY')
            )
            logger.info("RAG engine initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing RAG engine: {e}")
            raise
    return _rag_engine

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/status', methods=['GET'])
def status():
    """API endpoint to check service status"""
    try:
        # Check services
        services = document_processor.check_services()
        
        # Try to get RAG stats if initialized
        rag_stats = None
        try:
            rag = get_rag_engine()
            rag_stats = rag.get_stats()
        except Exception as e:
            logger.warning(f"Could not get RAG stats: {e}")
        
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'services': services,
            'rag_stats': rag_stats
        })
    except Exception as e:
        logger.error(f"Error checking status: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/query', methods=['POST'])
def query_papers():
    """API endpoint to query papers using RAG"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'status': 'error',
                'error': 'No query provided'
            }), 400
        
        query = data.get('query')
        paper_ids = data.get('paper_ids')  # Optional: limit to specific papers
        n_results = data.get('n_results', 5)
        
        logger.info(f"Processing query: {query}")
        
        # Get RAG engine
        rag = get_rag_engine()
        
        # Query the RAG system
        result = rag.query(
            query=query,
            n_results=n_results,
            paper_ids=paper_ids
        )
        
        return jsonify({
            'status': 'ok',
            'result': result
        })
    
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/upload', methods=['POST'])
def upload_paper():
    """API endpoint to upload and ingest a paper into RAG system"""
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
                'error': f'Only PDF files are allowed for academic papers'
            }), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename_with_timestamp = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename_with_timestamp)
        
        file.save(file_path)
        logger.info(f"File saved: {file_path}")
        
        # Process file with GROBID
        paper_data = document_processor.process_file_for_rag(file_path)
        
        if 'error' in paper_data:
            return jsonify({
                'status': 'error',
                'error': paper_data['error']
            }), 400
        
        # Get RAG engine
        rag = get_rag_engine()
        
        # Ingest paper into RAG system
        ingest_result = rag.ingest_paper(paper_data)
        
        if not ingest_result.get('success'):
            return jsonify({
                'status': 'error',
                'error': ingest_result.get('error', 'Failed to ingest paper')
            }), 500
        
        return jsonify({
            'status': 'ok',
            'result': {
                'paper_id': ingest_result['paper_id'],
                'title': ingest_result['title'],
                'chunks_processed': ingest_result['chunks_processed'],
                'sections_processed': ingest_result['sections_processed'],
                'filename': filename,
                'upload_date': datetime.now().isoformat()
            }
        })
    
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/papers', methods=['GET'])
def list_papers():
    """API endpoint to list all uploaded papers"""
    try:
        rag = get_rag_engine()
        papers = rag.list_papers()
        
        return jsonify({
            'status': 'ok',
            'papers': papers,
            'total': len(papers)
        })
    
    except Exception as e:
        logger.error(f"Error listing papers: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/papers/<paper_id>', methods=['DELETE'])
def delete_paper(paper_id):
    """API endpoint to delete a paper"""
    try:
        rag = get_rag_engine()
        success = rag.delete_paper(paper_id)
        
        if success:
            return jsonify({
                'status': 'ok',
                'message': f'Paper {paper_id} deleted successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'error': 'Paper not found or could not be deleted'
            }), 404
    
    except Exception as e:
        logger.error(f"Error deleting paper: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/compare', methods=['POST'])
def compare_papers():
    """API endpoint to compare multiple papers"""
    try:
        data = request.get_json()
        
        if not data or 'paper_ids' not in data:
            return jsonify({
                'status': 'error',
                'error': 'No paper IDs provided'
            }), 400
        
        paper_ids = data.get('paper_ids')
        comparison_aspects = data.get('aspects', ['methodology', 'results', 'conclusions', 'limitations'])
        
        if not isinstance(paper_ids, list) or len(paper_ids) < 2:
            return jsonify({
                'status': 'error',
                'error': 'At least 2 paper IDs required for comparison'
            }), 400
        
        logger.info(f"Comparing papers: {paper_ids}")
        
        rag = get_rag_engine()
        result = rag.compare_papers(
            paper_ids=paper_ids,
            comparison_aspects=comparison_aspects
        )
        
        return jsonify({
            'status': 'ok',
            'result': result
        })
    
    except Exception as e:
        logger.error(f"Error comparing papers: {e}")
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