FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# First install numpy and scipy with compatible versions
RUN pip install --no-cache-dir numpy==1.24.2 scipy==1.10.1

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger')"

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