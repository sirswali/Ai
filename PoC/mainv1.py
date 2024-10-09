import os
from dotenv import load_dotenv
from src.slack.bot import SlackBot
from src.knowledge_base.kb import KnowledgeBase
from src.llm.wrapper import LLMWrapper
from src.jira.client import JiraClient
from src.utils.logger import AuditLogger
from src.utils.access_control import AccessControl
from src.utils.chat_memory import ChatMemory
from src.utils.data_lineage import DataLineage
from src.utils.bias_management import BiasManagement
from src.task_management.allocator import TaskAllocator

def initialize_components():
    """
    Initialize all the components required for the application.
    """
    load_dotenv()

    try:
        kb = KnowledgeBase()
        print(kb.get_storage_info())  # Print the current storage type being used

        llm = LLMWrapper()
        jira = JiraClient()
        logger = AuditLogger()
        access_control = AccessControl()
        chat_memory = ChatMemory()
        data_lineage = DataLineage()
        bias_management = BiasManagement()
        task_allocator = TaskAllocator(jira, llm)  # Pass LLM to TaskAllocator

        return {
            'kb': kb,
            'llm': llm,
            'jira': jira,
            'logger': logger,
            'access_control': access_control,
            'chat_memory': chat_memory,
            'data_lineage': data_lineage,
            'bias_management': bias_management,
            'task_allocator': task_allocator
        }
    except Exception as e:
        logger.error(f"Error initializing components: {e}")
        raise

def main():
    """
    Main function to start the Slack bot and register command handlers.
    """
    try:
        components = initialize_components()
        slack_bot = SlackBot(components)

        # Register handlers for various Slack commands
        slack_bot.app.command("/allocate_task")(slack_bot.handlers.handle_task_allocation)
        slack_bot.app.command("/workload_report")(slack_bot.handlers.handle_workload_report)
        slack_bot.app.command("/reallocate_tasks")(slack_bot.handlers.handle_task_reallocation)
        slack_bot.app.command("/kb_add")(slack_bot.handlers.handle_kb_add)
        slack_bot.app.command("/kb_search")(slack_bot.handlers.handle_kb_search)
        slack_bot.app.command("/kb_update")(slack_bot.handlers.handle_kb_update)
        slack_bot.app.command("/kb_delete")(slack_bot.handlers.handle_kb_delete)
        slack_bot.app.command("/kb_info")(slack_bot.handlers.handle_kb_info)

        # New commands for LLM functionalities
        slack_bot.app.command("/summarize")(slack_bot.handlers.handle_summarize)
        slack_bot.app.command("/semantic_search")(slack_bot.handlers.handle_semantic_search)

        slack_bot.start()
    except Exception as e:
        components['logger'].error(f"Error in main function: {e}")
    finally:
        # Ensure knowledge base data is persisted when the application exits
        components['kb'].persist()

if __name__ == "__main__":
    main()
```

### Key Improvements:
#1. **Error Handling**: Added try-except blocks to catch and log errors.
#2. **Logging**: Enhanced logging to capture errors during component initialization and in the main function.
#3. **Documentation**: Added docstrings to functions to explain their purpose.
#4. **Configuration Management**: Ensured that environment variables are loaded at the beginning of the `initialize_components` function.

#These improvements will make your code more robust, easier to maintain, and better documented.