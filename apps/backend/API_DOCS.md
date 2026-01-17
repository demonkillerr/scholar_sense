# Sentiment Analysis Backend API Documentation

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