from .kb import KnowledgeBase

__all__ = ['KnowledgeBase']

# Initialization code (if needed)
# For example, you might want to set up logging for the Knowledge Base module
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# You might also want to check if the ENCRYPTION_KEY is set in the environment
import os
if 'ENCRYPTION_KEY' not in os.environ:
    logging.warning("ENCRYPTION_KEY is not set in the environment. A new key will be generated for each KnowledgeBase instance.")