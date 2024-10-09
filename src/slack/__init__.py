from .bot import SlackBot
from .handlers import SlackHandlers

__all__ = ['SlackBot', 'SlackHandlers']

# Initialization code (if needed)
# For example, you might want to set up logging for the Slack module
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# You might also want to check if the necessary Slack tokens are set in the environment
import os
required_env_vars = ['SLACK_BOT_TOKEN', 'SLACK_SIGNING_SECRET', 'SLACK_APP_TOKEN']
missing_vars = [var for var in required_env_vars if var not in os.environ]
if missing_vars:
    logging.warning(f"The following required environment variables are not set: {', '.join(missing_vars)}")