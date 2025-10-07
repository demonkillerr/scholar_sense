#!/bin/bash

# Sentiment Analysis Backend Startup Script (Conda Version)
# This script starts the backend services for the sentiment analysis system using Conda

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Set environment variables
export PORT=5000
export DEBUG=true
export UPLOAD_FOLDER="./uploads"
export GROBID_URL="http://localhost:8070"

# Create necessary directories with full permissions
mkdir -p "$UPLOAD_FOLDER"
chmod 777 "$UPLOAD_FOLDER"

mkdir -p "./logs"
chmod 777 "./logs"

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "Error: Conda is not installed or not in PATH."
    echo "Please install Anaconda or Miniconda first."
    echo "Visit: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Check if sentiment environment exists, create if not
if ! conda env list | grep -q "sentiment"; then
    echo "Creating new conda environment 'sentiment'..."
    conda create -y -n sentiment python=3.9
    
    # Activate environment and install dependencies
    echo "Installing dependencies..."
    eval "$(conda shell.bash hook)"
    conda activate sentiment
    
    # Install specific versions of problematic packages first
    pip install numpy==1.23.5
    pip install scikit-learn==1.2.2
    pip install nltk==3.8.1
    
    # Then install remaining dependencies
    pip install -r requirements.txt
else
    echo "Using existing conda environment 'sentiment'..."
    eval "$(conda shell.bash hook)"
    conda activate sentiment
fi

# Check if GROBID is running
echo "Checking GROBID service..."
curl -s -o /dev/null -w "%{http_code}" $GROBID_URL > /dev/null
if [ $? -ne 0 ]; then
    echo "Warning: GROBID service is not available at $GROBID_URL"
    echo "Some PDF processing features may not work."
    echo "To start GROBID, run the grobid_deployment/deploy-grobid.sh script."
else
    echo "GROBID service is running."
fi

# Start the Flask application
echo "Starting Flask application on port $PORT..."
python app.py

# Note: This script will keep running until the Flask app is stopped
# To stop the app, press Ctrl+C 