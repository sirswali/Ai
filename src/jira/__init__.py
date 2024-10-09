from .client import JiraClient

__all__ = ['JiraClient']

# Initialization code (if needed)
# For example, you might want to set up logging for the Jira module
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())