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

Docker is the preferred method for setting up and running this project. It ensures a consistent environment across different systems and simplifies the setup process.

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ai-task-management.git
   cd ai-task-management
   ```

2. Create a `.env` file in the project root and add your environment variables (see Environment Variables section below).

3. Build the Docker image:
   ```
   ./docker_build.sh
   ```
   This script builds the Docker image, installing all necessary dependencies and setting up the environment as specified in the Dockerfile.

   Expected output:
   ```
   [+] Building 0.6s (10/10) FINISHED
    => [internal] load build definition from Dockerfile
    => => transferring dockerfile: 37B
    => [internal] load .dockerignore
    => => transferring context: 2B
    => [internal] load metadata for docker.io/library/python:3.12.7-bookworm
    => [1/5] FROM docker.io/library/python:3.12.7-bookworm
    => [internal] load build context
    => => transferring context: 32B
    => [2/5] WORKDIR /usr/src/app
    => [3/5] COPY requirements.txt ./
    => [4/5] RUN pip install --no-cache-dir --upgrade pip &&     pip install --no-cache-dir -r requirements.txt
    => [5/5] COPY . .
    => exporting to image
    => => exporting layers
    => => writing image sha256:...
    => => naming to docker.io/library/ai-task-management
   ```

   Troubleshooting:
   - If you encounter permission issues, try running the script with sudo: `sudo ./docker_build.sh`
   - If the script is not executable, run: `chmod +x docker_build.sh`

4. Run the container:
   ```
   docker run --env-file .env ai-task-management
   ```

   Expected output:
   ```
   Initializing AI-Powered Task Management System...
   Connected to database successfully
   Slack bot started
   JIRA integration initialized
   Admin GUI running on http://localhost:5000
   ```

   Troubleshooting:
   - If you see "Error: No such container", ensure you've built the image successfully in step 3.
   - If you encounter environment variable issues, check that your .env file is in the correct location and properly formatted.

5. Verify the setup:
   ```
   docker ps
   ```
   This command should show your running container.

   Expected output:
   ```
   CONTAINER ID   IMAGE               COMMAND                  CREATED          STATUS          PORTS     NAMES
   1234567890ab   ai-task-management  "python ./src/main.py"   10 seconds ago   Up 9 seconds              friendly_feynman
   ```

   Troubleshooting:
   - If you don't see your container, it may have exited. Use `docker ps -a` to see all containers, including stopped ones.
   - Check the logs with `docker logs <container_id>` to see any error messages.

6. Access the application:
   - Admin GUI: Open http://localhost:5000 in your web browser
   - Slack: The bot should now be active in your Slack workspace
   - JIRA: The system should be able to fetch and update JIRA tasks

The Docker setup process includes the following key steps:
- Installing all required dependencies
- Setting up the Python environment
- Running tests to ensure the environment is correctly configured

This approach guarantees that all developers and production environments have identical setups, minimizing "it works on my machine" issues.

Additional Docker commands:
- Stop the container: `docker stop <container_id>`
- Remove the container: `docker rm <container_id>`
- Remove the image: `docker rmi ai-task-management`
- View logs: `docker logs <container_id>`

Troubleshooting tips:
- If you're having network issues, ensure Docker has the necessary permissions and that no firewall is blocking it.
- For performance issues, check your Docker resource allocation in Docker Desktop settings.
- If changes to your code are not reflected, make sure you've rebuilt the image after making changes.

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
