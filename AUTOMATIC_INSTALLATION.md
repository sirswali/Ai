# Automatic Installation

This guide provides instructions for automatically installing the AI-Powered Task Management and Knowledge Base System using pip.

## Installation

You can install this project directly from the repository using pip:

```
pip install git+https://github.com/yourusername/ai-task-management.git
```

This command will install the project and all its dependencies.

## Running the Application

After installation, you can run the application using:

```
run-task-management
```

To run the chat interface, use:

```
run-chat-interface
```

## Environment Variables

Before running the application, make sure to set up your environment variables. Create a `.env` file in your working directory with the following variables:

```
DEBUG=True
DATABASE_URL=postgresql://user:password@db:5432/dbname
SECRET_KEY=your_secret_key_change_this_in_production
SLACK_TOKEN=your_slack_token_here
JIRA_TOKEN=your_jira_token_here
CHAT_WINDOW_TITLE=Multi-Agent Task Management Chat
CHAT_WINDOW_WIDTH=500
CHAT_WINDOW_HEIGHT=600
AUTHOR_NAME=Your Name
AUTHOR_EMAIL=your.email@example.com
USE_TEST_DB=True  # Set to False to use external services
```

Adjust the values according to your setup and requirements.

## Additional Information

For more detailed information about the project, including its features, setup instructions for Docker and manual installation, and how to contribute, please refer to the main README.md file in the project repository.