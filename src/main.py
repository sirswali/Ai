import os
import sqlite3
from dotenv import load_dotenv
from slack.bot import SlackBot
# from knowledge_base.kb import KnowledgeBase  # Commented out
from llm.wrapper import LLMWrapper
from jira.client import JiraClient
from utils.logging.logger import CustomLogger, AuditLogger
from utils.security.access_control import AccessControl
from utils.data.chat_memory import ChatMemory
from utils.data.data_lineage import DataLineage
from utils.ai.bias_management import BiasManagementMasterAgent
from utils.ai.multi_agent import MasterAgent, Agent
from task_management.allocator import TaskAllocator
import config
from config import USE_TEST_DB, TEST_DB_PATH
from scripts.create_test_db import create_test_database

class ApplicationError(Exception):
    """Custom exception class for application-specific errors."""
    pass

def initialize_components():
    load_dotenv()
    
    logger = CustomLogger('MainApp').get_logger()
    logger.info("Initializing components...")
    
    try:
        if USE_TEST_DB:
            create_test_database()
            logger.info(f"Using test database at {TEST_DB_PATH}")
            # kb = KnowledgeBase(TEST_DB_PATH)  # Commented out
            jira = JiraClient(TEST_DB_PATH)
            chat_memory = ChatMemory(config.CHAT_MEMORY_EXPIRATION, storage_path=TEST_DB_PATH)
            data_lineage = DataLineage(TEST_DB_PATH)
            bias_management = BiasManagementMasterAgent(config.BIAS_THRESHOLD, storage_path=TEST_DB_PATH)
        else:
            logger.info("Using production environment")
            # kb = KnowledgeBase(config.KB_STORAGE_PATH)  # Commented out
            jira = JiraClient()
            chat_memory = ChatMemory(config.CHAT_MEMORY_EXPIRATION)
            data_lineage = DataLineage(config.DATA_LINEAGE_STORAGE)
            bias_management = BiasManagementMasterAgent(config.BIAS_THRESHOLD)
        
        # logger.info(kb.get_storage_info())  # Commented out
        
        llm = LLMWrapper(config.LLM_MODEL_NAME)
        audit_logger = AuditLogger(config.LOG_FILE_PATH)
        access_control = AccessControl(config.ACCESS_CONTROL_CONFIG)
        task_allocator = TaskAllocator(jira, llm, bias_management)
        
        master_agent = MasterAgent()
        task_allocation_agent = Agent("task_allocation", task_allocator.allocate_task)
        master_agent.add_agent(task_allocation_agent)
        
        logger.info("All components initialized successfully.")
        
        return {
            # 'kb': kb,  # Commented out
            'llm': llm,
            'jira': jira,
            'logger': logger,
            'audit_logger': audit_logger,
            'access_control': access_control,
            'chat_memory': chat_memory,
            'data_lineage': data_lineage,
            'bias_management': bias_management,
            'master_agent': master_agent,
            'task_allocator': task_allocator
        }
    except Exception as e:
        logger.error(f"Error initializing components: {str(e)}")
        raise ApplicationError(f"Failed to initialize components: {str(e)}")

def register_slack_handlers(slack_bot):
    # Task Management
    slack_bot.app.command("/allocate_task")(slack_bot.handlers.handle_bias_aware_task_allocation)
    slack_bot.app.command("/workload_report")(slack_bot.handlers.handle_workload_report)
    slack_bot.app.command("/reallocate_tasks")(slack_bot.handlers.handle_task_reallocation)
    slack_bot.app.command("/analyze_task")(slack_bot.handlers.handle_task_analysis)
    slack_bot.app.command("/match_task")(slack_bot.handlers.handle_task_matching)
    slack_bot.app.command("/recent_activities")(slack_bot.handlers.handle_recent_activities)
    
    # Knowledge Base (commented out)
    # slack_bot.app.command("/kb_add")(slack_bot.handlers.handle_kb_add)
    # slack_bot.app.command("/kb_search")(slack_bot.handlers.handle_kb_search)
    # slack_bot.app.command("/kb_update")(slack_bot.handlers.handle_kb_update)
    # slack_bot.app.command("/kb_delete")(slack_bot.handlers.handle_kb_delete)
    # slack_bot.app.command("/kb_info")(slack_bot.handlers.handle_kb_info)
    
    # LLM functionalities
    slack_bot.app.command("/summarize")(slack_bot.handlers.handle_summarize)
    slack_bot.app.command("/semantic_search")(slack_bot.handlers.handle_semantic_search)
    
    # Project Management
    slack_bot.app.command("/sprint_planning")(slack_bot.handlers.handle_sprint_planning)
    slack_bot.app.command("/progress_report")(slack_bot.handlers.handle_progress_report)
    slack_bot.app.command("/bug_report")(slack_bot.handlers.handle_bug_report)
    slack_bot.app.command("/feature_request")(slack_bot.handlers.handle_feature_request)
    slack_bot.app.command("/code_review")(slack_bot.handlers.handle_code_review)
    slack_bot.app.command("/ci_cd_status")(slack_bot.handlers.handle_ci_cd_status)
    slack_bot.app.command("/retrospective")(slack_bot.handlers.handle_retrospective)
    slack_bot.app.command("/release_planning")(slack_bot.handlers.handle_release_planning)

    # New monitoring handlers
    slack_bot.app.command("/monitor_slack")(slack_bot.handlers.handle_monitor_slack)
    slack_bot.app.command("/monitor_jira")(slack_bot.handlers.handle_monitor_jira)

def main():
    try:
        components = initialize_components()
        logger = components['logger']
        
        slack_bot = SlackBot(components, config.SLACK_BOT_TOKEN, config.SLACK_SIGNING_SECRET)
        
        register_slack_handlers(slack_bot)
        
        logger.info("Starting Slack bot...")
        slack_bot.start()
    except ApplicationError as ae:
        logger.error(f"Application error: {str(ae)}")
        # Perform any necessary cleanup or notification
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        # Perform any necessary cleanup or notification
    finally:
        try:
            # Ensure knowledge base data is persisted when the application exits
            # components['kb'].persist()  # Commented out
            logger.info("Application shutting down.")
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")

if __name__ == "__main__":
    main()
