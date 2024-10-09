from .allocator import TaskAllocator

__all__ = ['TaskAllocator']

# Initialization code (if needed)
# For example, you might want to set up logging for the Task Management module
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# You might also want to check if the necessary components (JiraClient and LLMWrapper) are available
try:
    from ..jira import JiraClient
    from ..llm import LLMWrapper
except ImportError as e:
    logging.warning(f"Error importing required components: {e}. Make sure Jira and LLM modules are properly set up.")

# Check if the storage file for task allocation history exists
import os
if not os.path.exists('task_allocation_history.json'):
    logging.info("Task allocation history file not found. A new one will be created when tasks are allocated.")