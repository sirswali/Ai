from .wrapper import LLMWrapper

__all__ = ['LLMWrapper']

# Initialization code (if needed)
# For example, you might want to set up logging for the LLM module
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# You might also want to check if the LLM_MODEL_NAME is set in the environment
import os
if 'LLM_MODEL_NAME' not in os.environ:
    logging.info("LLM_MODEL_NAME is not set in the environment. Using default model: EleutherAI/gpt-neo-1.3B")

# Check for CUDA availability
import torch
if torch.cuda.is_available():
    logging.info("CUDA is available. GPU will be used for LLM operations.")
else:
    logging.warning("CUDA is not available. CPU will be used for LLM operations, which may be slower.")