import os
import logging
import sys

def setup_logging():
    """Configure logging for the application"""
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

    # Create formatters
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create handlers
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add our handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Test logging
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    return logger 