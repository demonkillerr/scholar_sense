# ScholarSense API Documentation

## Overview
ScholarSense provides a RESTful API for academic paper analysis using Retrieval-Augmented Generation (RAG). Upload PDF papers, query them with natural language questions, and receive citation-grounded answers.

## Base URL
```
http://localhost:5000
```

## Authentication
Currently no authentication required (add for production).

---

## Endpoints

### 1. System Status

#### GET `/status`
Check system health and RAG statistics.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-11-14T10:30:00",
  "services": {
    "grobid": {
      "available": true,
      "url": "http://localhost:8070"
    }
  },
  "rag_stats": {
    "total_papers": 5,
    "total_chunks": 450,
    "embedding_model": "BAAI/bge-large-en-v1.5",
    "embedding_dimension": 1024,
    "llm_model": "gemini-pro"
  }
}
```

---

### 2. Upload Paper

#### POST `/upload`
Upload and ingest an academic PDF paper into the RAG system.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (PDF file)

**Response:**
```json
{
  "status": "ok",
  "result": {
    "paper_id": "abc123def456...",
    "title": "Attention Is All You Need",
    "chunks_processed": 45,
    "sections_processed": 7,
    "filename": "transformer_paper.pdf",
    "upload_date": "2025-11-14T10:35:00"
  }
}
```

---

### 3. Query Papers

#### POST `/query`
Query uploaded papers using natural language.

**Request:**
```json
{
  "query": "What are the main advantages of transformers over RNNs?",
  "paper_ids": ["abc123", "def456"],  // Optional: specific papers
  "n_results": 5  // Optional: number of context chunks (default: 5)
}
```

**Response:**
```json
{
  "status": "ok",
  "result": {
    "answer": "Transformers offer several advantages over RNNs [1][2]...",
    "citations": [
      {
        "citation_number": 1,
        "paper_title": "Attention Is All You Need",
        "section": "Introduction",
        "page": "2",
        "paper_id": "abc123"
      }
    ],
    "contexts": [
      {
        "text": "Unlike RNNs, transformers can process...",
        "metadata": {
          "paper_id": "abc123",
          "title": "Attention Is All You Need",
          "section": "Introduction",
          "page": "2"
        },
        "relevance_score": 0.89
      }
    ],
    "model": "gemini-pro",
    "contexts_used": 5
  }
}
```

---

### 4. List Papers

#### GET `/papers`
List all uploaded papers.

**Response:**
```json
{
  "status": "ok",
  "papers": [
    {
      "paper_id": "abc123",
      "title": "Attention Is All You Need",
      "authors": "Vaswani et al.",
      "year": "2017",
      "upload_date": "2025-11-14T10:35:00"
    }
  ],
  "total": 1
}
```

---

### 5. Delete Paper

#### DELETE `/papers/<paper_id>`
Delete a paper from the system.

**Response:**
```json
{
  "status": "ok",
  "message": "Paper abc123 deleted successfully"
}
```

---

### 6. Compare Papers

#### POST `/compare`
Compare multiple papers across different aspects.

**Request:**
```json
{
  "paper_ids": ["abc123", "def456", "ghi789"],
  "aspects": ["methodology", "results", "conclusions", "limitations"]
}
```

**Response:**
```json
{
  "status": "ok",
  "result": {
    "comparison": "Paper 1 and Paper 2 both use transformer architectures...",
    "papers_compared": 3,
    "aspects": ["methodology", "results", "conclusions", "limitations"],
    "model": "gemini-pro",
    "papers": [
      {
        "paper_id": "abc123",
        "title": "Attention Is All You Need",
        "abstract": "..."
      }
    ]
  }
}
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "status": "error",
  "error": "Error message description"
}
```

**Common HTTP Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `413 Payload Too Large` - File too large
- `500 Internal Server Error` - Server error

---

## Example Usage

### Python

```python
import requests

# Upload a paper
with open('paper.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/upload',
        files={'file': f}
    )
    paper_data = response.json()
    paper_id = paper_data['result']['paper_id']

# Query the paper
response = requests.post(
    'http://localhost:5000/query',
    json={
        'query': 'What is the main contribution of this paper?',
        'paper_ids': [paper_id]
    }
)
answer = response.json()['result']['answer']
print(answer)
```

### cURL

```bash
# Upload paper
curl -X POST http://localhost:5000/upload \
  -F "file=@paper.pdf"

# Query papers
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the key findings?"}'

# List papers
curl http://localhost:5000/papers
```

---

## Old Sentiment Analysis API (Deprecated)

This document provides detailed information about the sentiment analysis backend API for frontend developers.

## Basic Information

- Base URL: `http://localhost:5000`
- Content-Type for all POST requests should be: `application/json`
- All responses are in JSON format

## API Endpoints

### 1. Analyze Text or File

**Endpoint:** `/analyse`

**Method:** POST

**Description:** Analyze the sentiment of text content or uploaded files

**Request Body:**

Analyze text:
```json
{
  "text": "Text content to analyze",
  "title": "Optional text title",
  "method": "vader|textblob|combined",
  "full_analysis": false
}
```

Analyze file:
```json
{
  "file_path": "path/to/uploaded/file"
}
```

Analyze topic-based content:
```json
{
  "topic": "Topic to analyze",
  "file_path": "path/to/uploaded/file"
}
```

**Success Response:**
```json
{
  "status": "ok",
  "result": {
    "sentiment": "positive|negative|neutral",
    "score": 0.75,
    "confidence": 0.85,
    "details": {
      "pos": 0.8,
      "neg": 0.1,
      "neu": 0.1,
      "compound": 0.75
    }
  }
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": "Error message"
}
```

### 2. Upload File

**Endpoint:** `/upload`

**Method:** POST

**Description:** Upload a file for subsequent analysis

**Request Body:** 
- Use `multipart/form-data` format
- File field name should be `file`
- Supported file types: PDF, TXT, JSON

**Success Response:**
```json
{
  "status": "ok",
  "message": "File uploaded successfully",
  "file_path": "path/to/uploaded/file",
  "file_name": "Original file name",
  "file_type": "File type"
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": "Error message"
}
```

### 3. Access Uploaded File

**Endpoint:** `/files/<filename>`

**Method:** GET

**Description:** Get an uploaded file

**Parameters:**
- `filename`: Name of the uploaded file

**Response:** File content

### 4. Check Service Status

**Endpoint:** `/status`

**Method:** GET

**Description:** Check backend service status and dependencies

**Success Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-03-21T10:00:00",
  "services": {
    "grobid": {
      "available": true,
      "url": "http://localhost:8070"
    }
  }
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": "Error message",
  "timestamp": "2024-03-21T10:00:00"
}
```

### 5. Analyze Topic

**Endpoint:** `/analyze_topic`

**Method:** POST

**Description:** Analyze the sentiment of topic-related text

**Request Body:**
```json
{
  "topic": "Topic text to analyze"
}
```

**Success Response:**
```json
{
  "status": "ok",
  "result": {
    "topic": "Topic text",
    "sentiment": "positive|negative|neutral",
    "score": 0.75,
    "confidence": 0.85,
    "keywords": [
      {
        "word": "keyword1",
        "count": 5
      }
    ],
    "sample_text": "Sample text related to the topic..."
  }
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": "Error message"
}
```

## Usage Examples

### Example 1: Analyze Text

```javascript
// Frontend code example
async function analyzeText(text) {
  const response = await fetch('http://localhost:5000/analyse', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ 
      text,
      method: 'combined',
      full_analysis: false
    }),
  });
  
  const data = await response.json();
  if (data.status === 'ok') {
    return data.result;
  } else {
    throw new Error(data.error);
  }
}
```

### Example 2: Upload and Analyze File

```javascript
// Frontend code example
async function uploadAndAnalyzeFile(file) {
  // Upload file
  const formData = new FormData();
  formData.append('file', file);
  
  const uploadResponse = await fetch('http://localhost:5000/upload', {
    method: 'POST',
    body: formData,
  });
  
  const uploadData = await uploadResponse.json();
  if (uploadData.status !== 'ok') {
    throw new Error(uploadData.error);
  }
  
  // Analyze uploaded file
  const analyzeResponse = await fetch('http://localhost:5000/analyse', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ 
      file_path: uploadData.file_path,
      full_analysis: true
    }),
  });
  
  const analyzeData = await analyzeResponse.json();
  if (analyzeData.status === 'ok') {
    return analyzeData.result;
  } else {
    throw new Error(analyzeData.error);
  }
}
```

## Error Codes
- 400: Bad Request - Invalid input data
- 404: Not Found - Resource not found
- 413: Payload Too Large - File size exceeds limit
- 500: Internal Server Error - Server-side error

## Rate Limiting
- Maximum file size: 16MB
- Supported file types: PDF, TXT, JSON
- Concurrent requests: Limited by server configuration

## Security Considerations
1. All file uploads are validated for type and size
2. File paths are sanitized to prevent directory traversal
3. CORS is enabled for frontend access
4. File content is validated before processing 