#!/bin/bash

# Sentiment Analysis Backend Startup Script
# This script starts the backend services for the sentiment analysis system

# Set environment variables
export PORT=5000
export DEBUG=true
export UPLOAD_FOLDER="./uploads"
export GROBID_URL="http://localhost:8070"

# Create necessary directories
mkdir -p $UPLOAD_FOLDER

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if GROBID is running
echo "Checking GROBID service..."
curl -s -o /dev/null -w "%{http_code}" $GROBID_URL > /dev/null
if [ $? -ne 0 ]; then
    echo "Warning: GROBID service is not available at $GROBID_URL"
    echo "Some PDF processing features may not work."
    echo "To start GROBID, run the deploy-grobid.sh script."
else
    echo "GROBID service is running."
fi

# Start the Flask application
echo "Starting Flask application on port $PORT..."
python app.py

# Note: This script will keep running until the Flask app is stopped
# To stop the app, press Ctrl+C 