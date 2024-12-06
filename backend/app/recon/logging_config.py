import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging(log_dir: str = "logs"):
    """Configure logging system for the application."""
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(context)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # Create handlers
    # File handler for detailed logging
    detailed_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'detailed.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    detailed_handler.setFormatter(detailed_formatter)
    detailed_handler.setLevel(logging.DEBUG)

    # File handler for errors
    error_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'errors.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setFormatter(detailed_formatter)
    error_handler.setLevel(logging.ERROR)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(simple_formatter)
    console_handler.setLevel(logging.INFO)

    # Create logger
    logger = logging.getLogger('recon')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(detailed_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

    return logger

def log_with_context(logger, level: str, message: str, context: dict = None):
    """Log a message with additional context."""
    if context is None:
        context = {}
    
    context['timestamp'] = datetime.now().isoformat()
    
    log_method = getattr(logger, level.lower())
    log_method(message, extra={'context': str(context)})
