# Sentiment Analysis Backend Service

## Project Overview
A Flask-based sentiment analysis backend service that provides text and document sentiment analysis capabilities. The service supports multiple file formats (PDF, TXT, JSON) and can perform topic-based text analysis.

## Technology Stack
- **Python 3.8+**: Main programming language
- **Flask**: Web framework
- **NLTK**: Natural Language Processing toolkit
- **TextBlob**: Text analysis library
- **GROBID**: PDF document parsing service
- **scikit-learn**: Machine learning library for text feature extraction
- **Flask-CORS**: Cross-origin resource sharing handler

## Project Structure
```
backend/
├── API_DOCS.md          # API documentation
├── grobid_deployment     # GROBID deployment 
│   ├─ deploy-grobid.sh
│   ├─ grobid-api-example.py
│   └─ grobid-docker-deployment.md
├── app.py                 # Main application entry point
├── document_processor.py  # Document processing module
├── sentiment_analyzer.py  # Sentiment analysis module
├── text_processor.py     # Text processing module
├── logging_config.py     # Logging configuration module
├── requirements.txt      # Project dependencies
├── start_conda.sh       # Startup script
├── uploads/             # Uploaded files directory
└── logs/               # Log files directory
```

## Environment Requirements
- Python 3.8 or higher
- [Conda](https://docs.conda.io/en/latest/) environment manager
- [GROBID](https://grobid.readthedocs.io/en/latest/) service (for PDF processing)

## Deployment Steps

1. Deploy GROBID service:
The full instructions are available in the [grobid_deployment/grobid-docker-deployment.md](grobid_deployment/grobid-docker-deployment.md) file.
```bash
cd grobid_deployment
./deploy-grobid.sh
```
Check GROBID service status:
```bash
curl http://localhost:8070/api/isalive
```

2. Start the sentiment analysis service:
```bash
./start_conda.sh
```

## Configuration
- `UPLOAD_FOLDER`: Directory for uploaded files (default: 'uploads')
- `MAX_CONTENT_LENGTH`: Maximum file size limit (default: 16MB)
- `ALLOWED_EXTENSIONS`: Allowed file types (pdf, txt, text, json)
- `LOG_DIR`: Directory for log files (default: 'logs')


## API Endpoints

### 1. Status Check
- **URL**: `/status`
- **Method**: GET
- **Description**: Check service status and dependency availability

### 2. Text Analysis
- **URL**: `/analyse`
- **Method**: POST
- **Features**:
  - Text sentiment analysis
  - File processing
  - Topic-based analysis

### 3. File Upload
- **URL**: `/upload`
- **Method**: POST
- **Feature**: Upload and analyze files

### 4. File Retrieval
- **URL**: `/files/<filename>`
- **Method**: GET
- **Feature**: Retrieve uploaded files

### 5. Topic Analysis
- **URL**: `/analyze_topic`
- **Method**: POST
- **Feature**: Analyze text topics and keywords

## Logging System
- Log file location: `logs/app.log`
- Log level: INFO
- Log format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## Error Handling
The service includes the following error handling:
- 413: File size limit exceeded
- 404: Resource not found
- 500: Internal server error

## Development Notes
1. Ensure `DEBUG=True` is set in development environment
2. Run service directly using `python app.py`
3. Logs are output to both console and file

## Important Notes
1. Ensure GROBID service is running properly
2. Regularly clean temporary files in the `uploads` directory
3. Monitor log file size and rotate when necessary
4. Set appropriate file size limits in production environment

## Troubleshooting
1. If service fails to start, check:
   - Conda environment is properly activated
   - All dependencies are correctly installed
   - GROBID service is running
   - Port is not in use

2. If file upload fails, check:
   - File size is within limits
   - File type is allowed
   - Upload directory permissions are correct

3. If analysis fails, check:
   - Error messages in log file
   - Input text format is correct
   - GROBID service is responding properly 