import logging
import sys
from datetime import datetime
from backend.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("ai_governance")


def log_request(method: str, path: str, user_email: str = None, status_code: int = None):
    """Log API request"""
    logger.info(f"Request: {method} {path} | User: {user_email or 'anonymous'} | Status: {status_code}")


def log_error(error: Exception, context: str = ""):
    """Log error with context"""
    logger.error(f"Error in {context}: {str(error)}", exc_info=True)


def log_security_event(event_type: str, user_email: str, details: str = ""):
    """Log security-related events"""
    logger.warning(f"Security Event: {event_type} | User: {user_email} | Details: {details}")
