FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install Python 3.10 and build essentials
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3.10-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create symlink for python command
RUN ln -s /usr/bin/python3.10 /usr/bin/python

# First install numpy and scipy with compatible versions
RUN pip install --no-cache-dir numpy==1.24.2 scipy==1.10.1

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger')"

# Pre-download embedding model to avoid runtime download
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-large-en-v1.5')"

# Copy application code
COPY . .

# Create upload directory
RUN mkdir -p uploads logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=5000
# Default GROBID URL, can be overridden at runtime
ENV GROBID_URL=http://grobid-service:8070

# Expose port
EXPOSE 5000

# Start application
CMD ["python", "app.py"] 