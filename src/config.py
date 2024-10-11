import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration settings for the AI project

# Environment settings
USE_TEST_DB = os.getenv("USE_TEST_DB", "False").lower() == "true"
TEST_DB_PATH = os.path.join(os.getcwd(), "test_database.db")

# LLM settings
LLM_MODEL_NAME = "EleutherAI/gpt-neo-1.3B"

# Slack settings
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

# Jira settings
JIRA_URL = "https://your-domain.atlassian.net"
JIRA_USERNAME = "your_jira_username"
JIRA_API_TOKEN = "your_jira_api_token"

# Knowledge Base settings
KB_STORAGE_PATH = "knowledge_base"

# Logging settings
LOG_LEVEL = "INFO"
LOG_FILE_PATH = "app.log"

# Access Control settings
ACCESS_CONTROL_CONFIG = {
    "admin_users": ["user1", "user2"],
    "allowed_channels": ["channel1", "channel2"]
}

# Data Lineage settings
DATA_LINEAGE_STORAGE = "path/to/data_lineage_storage"

# Bias Management settings
BIAS_THRESHOLD = 0.7

# Chat Memory settings
CHAT_MEMORY_EXPIRATION = 3600  # in seconds