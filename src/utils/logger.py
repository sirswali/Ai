import logging
import os
from logging.handlers import RotatingFileHandler

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

    def log_interaction(self, user_id, query, response):
        self.logger.info(f"User: {user_id}, Query: {query}, Response: {response}")

    def log_feedback(self, user_id, response, feedback):
        self.logger.info(f"User: {user_id}, Response: {response}, Feedback: {feedback}")

# Usage example
if __name__ == "__main__":
    logger = CustomLogger(__name__).get_logger()
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    audit_logger = AuditLogger()
    audit_logger.log_interaction("user123", "What's the weather?", "The weather is sunny.")
    audit_logger.log_feedback("user123", "The weather is sunny.", "helpful")