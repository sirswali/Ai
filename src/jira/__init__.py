"""
JIRA integration module using local endpoint schemas.
This module provides a JiraClient that works with predefined JIRA endpoint schemas
rather than using an external JIRA library.
"""

from .client import JiraClient

__all__ = ['JiraClient']

# Set up null handler to avoid "No handler found" warnings
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
