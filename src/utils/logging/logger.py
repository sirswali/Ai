import logging
from logging.handlers import RotatingFileHandler
import os

class CustomLogger:
    def __init__(self, name, log_file='app.log', level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)

        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = RotatingFileHandler(f'logs/{log_file}', maxBytes=10*1024*1024, backupCount=5)

        # Create formatters and add it to handlers
        c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        # Add handlers to the logger
        self.logger.addHandler(c_handler)
        self.logger.addHandler(f_handler)

    def get_logger(self):
        return self.logger

class AuditLogger(CustomLogger):
    def __init__(self, log_file='audit.log', level=logging.INFO):
        super().__init__('AuditLogger', log_file, level)

    def log_action(self, user, action, details):
        self.logger.info(f"User: {user} | Action: {action} | Details: {details}")

# Usage example:
# logger = CustomLogger('MyApp').get_logger()
# logger.info('This is an info message')
# 
# audit_logger = AuditLogger()
# audit_logger.log_action('user123', 'CREATE_TASK', 'Created task XYZ')