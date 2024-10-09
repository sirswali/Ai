from .access_control import AccessControl
from .bias_management import BiasManagement
from .chat_memory import ChatMemory
from .data_lineage import DataLineage
from .logger import CustomLogger, AuditLogger

__all__ = ['AccessControl', 'BiasManagement', 'ChatMemory', 'DataLineage', 'CustomLogger', 'AuditLogger']

# Initialization code
import logging
import os

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create necessary directories
directories = ['logs', 'data']
for directory in directories:
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created directory: {directory}")

# Check for necessary environment variables
required_env_vars = ['ALLOWED_USERS', 'ENCRYPTION_KEY']
missing_vars = [var for var in required_env_vars if var not in os.environ]
if missing_vars:
    logging.warning(f"The following required environment variables are not set: {', '.join(missing_vars)}")

# Initialize global instances if needed
# For example:
# global_access_control = AccessControl()
# global_bias_management = BiasManagement()
# global_chat_memory = ChatMemory()
# global_data_lineage = DataLineage()
# global_logger = CustomLogger('GlobalLogger')
# global_audit_logger = AuditLogger()

logging.info("Utils module initialized successfully")