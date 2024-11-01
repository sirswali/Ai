"""
Enhanced logging module with basic and essential audit capabilities.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional, Dict, Any

class CustomLogger:
    def __init__(self, name, log_file='app.log', level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create logs directory if it doesn't exist
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Create handlers
        file_handler = RotatingFileHandler(os.path.join(log_dir, log_file), maxBytes=10485760, backupCount=5)
        console_handler = logging.StreamHandler()

        # Create formatters and add it to handlers
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        console_handler.setFormatter(console_format)

        # Add handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger

class AuditLogger(CustomLogger):
    def __init__(self):
        super().__init__('AuditLogger', 'audit.log')

    def log_interaction(self, user_id: str, query: str, response: str) -> None:
        """Log basic user interaction"""
        self.logger.info(f"User: {user_id}, Query: {query}, Response: {response}")

    def log_feedback(self, user_id: str, response: str, feedback: str) -> None:
        """Log user feedback"""
        self.logger.info(f"User: {user_id}, Response: {response}, Feedback: {feedback}")

    def log_thread_event(self, event_type: str, thread_id: str, details: Dict[str, Any]) -> None:
        """
        Log Slack thread-related events with essential details
        
        Args:
            event_type: Type of thread event (created, updated, closed)
            thread_id: Unique identifier for the thread
            details: Additional event details (user_id, channel_id, etc.)
        """
        event_info = {
            'timestamp': datetime.utcnow().isoformat(),
            'thread_id': thread_id,
            'type': event_type,
            **details
        }
        self.logger.info(f"Thread Event: {event_info}")

    def log_security_event(self, event_type: str, user_id: Optional[str], details: Dict[str, Any]) -> None:
        """
        Log security-related events
        
        Args:
            event_type: Type of security event
            user_id: Associated user ID (if applicable)
            details: Additional security event details
        """
        event_info = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': event_type,
            'user_id': user_id,
            **details
        }
        self.logger.warning(f"Security Event: {event_info}")

# Usage example
if __name__ == "__main__":
    logger = CustomLogger(__name__).get_logger()
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    audit_logger = AuditLogger()
    
    # Basic logging examples
    audit_logger.log_interaction("user123", "What's the weather?", "The weather is sunny.")
    audit_logger.log_feedback("user123", "The weather is sunny.", "helpful")
    
    # Thread event logging example
    audit_logger.log_thread_event(
        "thread_created",
        "thread123",
        {
            "user_id": "user123",
            "channel_id": "channel456",
            "initial_message": "Hello"
        }
    )
    
    # Security event logging example
    audit_logger.log_security_event(
        "unauthorized_access_attempt",
        "user123",
        {
            "resource": "admin_panel",
            "ip_address": "192.168.1.1",
            "status": "blocked"
        }
    )
