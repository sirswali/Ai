# AI-Powered Task Management and Knowledge Base System

This project implements an AI-powered task management and knowledge base system that integrates with Slack and JIRA. It uses Large Language Models (LLMs) to optimize task allocation, provide intelligent responses to queries, and manage a knowledge base.

## Project Structure

```
.
├── src/
│   ├── admin_gui/
│   │   ├── templates/
│   │   │   ├── edit_user.html
│   │   │   ├── edit_role.html
│   │   │   ├── role_management.html
│   │   │   ├── permission_management.html
│   │   │   ├── access_logs.html
│   │   │   └── ...
│   │   ├── static/
│   │   │   ├── css/
│   │   │   │   └── style.css
│   │   │   └── js/
│   │   │       └── script.js
│   │   ├── app.py
│   │   └── create_tables.sql
│   ├── jira/
│   │   └── client.py
│   ├── knowledge_base/
│   │   └── kb.py
│   ├── llm/
│   │   └── wrapper.py
│   ├── slack/
│   │   ├── bot.py
│   │   └── handlers.py
│   ├── task_management/
│   │   └── allocator.py
│   ├── utils/
│   │   ├── access_control.py
│   │   ├── bias_management.py
│   │   ├── chat_memory.py
│   │   ├── data_lineage.py
│   │   ├── logger.py
│   │   └── monitoring_agent.py
│   ├── config.py
│   ├── main.py
│   ├── demo.py
│   └── create_test_db.py
├── tests/
│   ├── test_main.py
│   ├── test_task_allocator.py
│   ├── test_knowledge_base.py
│   ├── test_llm_wrapper.py
│   └── test_suite.py
├── bias_managent_mutliagent_poc.py
├── chat_interface.py
├── requirements.txt
├── setup.py
├── Dockerfile
├── entrypoint.sh
├── docker_build.sh
├── .env
├── .gitignore
└── README.md
```

## Setup

### Using Docker (Recommended)

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ai-task-management.git
   cd ai-task-management
   ```

2. Create a `.env` file in the project root and add your environment variables (see Environment Variables section below).

3. Build the Docker image:
   ```
   docker build -t ai-task-management .
   ```

4. Run the container:
   ```
   docker run --env-file .env ai-task-management
   ```

### Manual Setup

1. Clone the repository as described above.

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   pip install -e .
   ```

4. Create a `.env` file in the project root and add your environment variables.

## Environment Variables

Create a `.env` file in the project root with the following variables:

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

## Setting up the Test Database

To create a test database with dummy data for development and testing purposes:

1. Navigate to the `src` directory:
   ```
   cd src
   ```
2. Run the `create_test_db.py` script:
   ```
   python create_test_db.py
   ```
3. This will create a SQLite database file named `test_database.db` in the same directory.

The test database includes dummy data for users, tasks, comments, and knowledge base entries, allowing you to test various functionalities of the system without connecting to external services.

## Using the Test Database

To use the test database instead of connecting to external services:

1. In your `.env` file, set the `USE_TEST_DB` variable to `True`:
   ```
   USE_TEST_DB=True
   ```
2. When this variable is set to `True`, the application will use the SQLite test database for all storage operations.
3. To switch back to using external services, set `USE_TEST_DB=False` or remove the variable from your `.env` file.

## Running the Application

### Using Docker

To run the main application:
```
docker run --env-file .env ai-task-management run-task-management
```

To run the chat interface:
```
docker run --env-file .env ai-task-management run-chat-interface
```

### Manual Run

To start the main application, run:

```
python src/main.py
```

This will initialize all components and start the Slack bot.

To run the chat interface:
```
python chat_interface.py
```

## Running the Demo

To see a demonstration of the system's capabilities, run:

```
python src/demo.py
```

This script showcases the main functionalities of the system, including task allocation, knowledge base operations, LLM capabilities, and Slack integration.

## Running Tests

To run all tests, execute:

```
python tests/test_suite.py
```

This will run all test cases for the main application, task allocator, knowledge base, and LLM wrapper.

## Features

1. Task Management
   - Allocate tasks based on team members' skills
   - Generate workload reports
   - Reallocate tasks for optimal resource utilization

2. Knowledge Base
   - Add, update, delete, and search knowledge base entries
   - Semantic search capabilities

3. LLM Integration
   - Analyze tasks and match with team members' skills
   - Optimize task allocation
   - Summarize text and perform semantic search

4. Slack Integration
   - Interact with the system through Slack commands
   - Receive notifications and updates in Slack

5. JIRA Integration
   - Fetch and update task information from JIRA

6. Monitoring and Activity Tracking
   - Monitor Slack activity for specific users
   - Track updates and changes in JIRA projects

7. Admin GUI
   - Web-based interface for system administration

8. Bias Management
   - Multi-agent system for managing and mitigating biases in task allocation

## Slack Commands

Here's a list of available Slack commands:

- `/allocate_task`: Allocate a new task
- `/workload_report`: Generate a workload report
- `/reallocate_tasks`: Suggest task reallocation
- `/kb_add`: Add a new entry to the knowledge base
- `/kb_search`: Search the knowledge base
- `/kb_update`: Update an existing knowledge base entry
- `/kb_delete`: Delete a knowledge base entry
- `/kb_info`: Get information about the knowledge base
- `/summarize`: Summarize a given text
- `/semantic_search`: Perform a semantic search
- `/analyze_task`: Analyze task requirements
- `/match_task`: Match a task to team members
- `/recent_activities`: Get recent activities
- `/monitor_slack`: Monitor Slack activity for a user
- `/monitor_jira`: Monitor updates for a JIRA project

## Development

### Adding New Features

1. Implement your feature in the appropriate module under the `src/` directory.
2. Update or add tests in the `tests/` directory.
3. Update the README.md if your feature introduces new functionality or commands.
4. If your feature requires new dependencies, add them to `requirements.txt` and `setup.py`.

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Implement your changes
4. Write tests for your new feature
5. Ensure all tests pass
6. Submit a pull request

## License

[Insert your chosen license here]
