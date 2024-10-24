import os
import asyncio
import sqlite3
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from aiohttp import web
import aiojobs
from prometheus_client import Counter, Histogram, Gauge
import aioredis

from slack.bot import SlackBot
# from knowledge_base.kb import KnowledgeBase  # Commented out
from llm.wrapper import LLMWrapper
# from jira.client import JiraClient
from utils.logging.logger import CustomLogger, AuditLogger
# from utils.access_control import AccessControl
from utils.chat_memory import ChatMemory
from utils.data_lineage import DataLineage
# from utils.bias_management import BiasManagementMasterAgent
# from utils.multi_agent import MasterAgent, Agent
# from task_management.allocator import TaskAllocator
import config
from config import USE_TEST_DB, TEST_DB_PATH
from create_test_db import create_test_database

# Metrics setup
PROCESSED_MESSAGES = Counter('processed_messages_total', 'Number of processed messages')
PROCESSING_TIME = Histogram('message_processing_seconds', 'Time spent processing messages')
QUEUE_SIZE = Gauge('processing_queue_size', 'Current size of the processing queue')
ERROR_COUNTER = Counter('processing_errors_total', 'Number of processing errors')
AGENT_PROCESSING_TIME = Histogram('agent_processing_seconds', 'Time spent in multi-agent processing', ['agent_type'])

class ApplicationError(Exception):
    """Custom exception class for application-specific errors."""
    pass

@dataclass
class Message:
    """Message container with metadata"""
    id: str
    user_id: str
    content: str
    channel: str
    timestamp: float
    retries: int = 0
    max_retries: int = 3

class MultiAgentConfig:
    def __init__(self):
        self.model_name = config.LLM_MODEL_NAME if hasattr(config, 'LLM_MODEL_NAME') else "EleutherAI/gpt-neo-1.3B"
        self.max_tokens = 100
        self.cache_ttl = 3600
        self.retry_attempts = 3
        self.retry_delay = 1.0
        self.timeout = 30.0

class MultiAgentCircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=60):
        self.failures = 0
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.last_failure_time = 0
        self._lock = asyncio.Lock()
    
    def is_open(self) -> bool:
        if time.time() - self.last_failure_time > self.reset_timeout:
            self.reset()
            return False
        return self.failures >= self.failure_threshold
    
    async def call(self, func, *args, **kwargs):
        async with self._lock:
            if self.is_open():
                raise Exception("Circuit breaker is open")
            try:
                result = await func(*args, **kwargs)
                self.reset()
                return result
            except Exception as e:
                self.record_failure()
                raise e
    
    def reset(self):
        self.failures = 0
        self.last_failure_time = 0
    
    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()

class AsyncProcessingSystem:
    def __init__(self, components, redis_url: str = "redis://localhost", max_queue_size: int = 1000):
        self.components = components
        self.redis = aioredis.from_url(redis_url)
        self.processing_queue = asyncio.Queue(maxsize=max_queue_size)
        self.scheduler = aiojobs.Scheduler()
        self.shutdown_event = asyncio.Event()
        self.circuit_breaker = MultiAgentCircuitBreaker()
        self.config = MultiAgentConfig()
        self.logger = components['logger']
        self.input_module = InputModule()  # Initialize multi-agent system

    async def initialize(self):
        """Initialize async components"""
        await self.scheduler.spawn(self.monitor_system())
        await self.health_check()
        self.logger.info("Async processing system initialized")

    async def health_check(self) -> bool:
        """Perform system health check"""
        try:
            await self.redis.ping()
            test_message = Message(
                id="health_check",
                user_id="system",
                content="health_check",
                channel="system",
                timestamp=time.time()
            )
            result = await self.process_test_message(test_message)
            return result is not None
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False

    async def process_test_message(self, message: Message) -> bool:
        """Process a test message for health check"""
        try:
            async with AGENT_PROCESSING_TIME.labels('health_check').time():
                result = await asyncio.wait_for(
                    self.circuit_breaker.call(
                        self.input_module.orchestrator.process_query,
                        message.content,
                        message.user_id
                    ),
                    timeout=self.config.timeout
                )
            return result is not None
        except Exception:
            return False

    async def process_message(self, message: Message):
        """Process a message through the multi-agent system"""
        try:
            async with PROCESSING_TIME.time():
                result = await self.circuit_breaker.call(
                    self.input_module.orchestrator.process_query,
                    message.content,
                    message.user_id
                )
                
                # Cache result
                await self.redis.set(
                    f"result:{message.id}",
                    result,
                    ex=self.config.cache_ttl
                )
                
                PROCESSED_MESSAGES.inc()
                return result
                
        except Exception as e:
            ERROR_COUNTER.inc()
            self.logger.error(f"Error processing message: {str(e)}")
            if message.retries < message.max_retries:
                await self.requeue_with_backoff(message)
            raise

    async def requeue_with_backoff(self, message: Message):
        """Requeue a failed message with exponential backoff"""
        message.retries += 1
        delay = 2 ** message.retries
        await asyncio.sleep(delay)
        await self.processing_queue.put(message)

    async def monitor_system(self):
        """Monitor system metrics"""
        while not self.shutdown_event.is_set():
            try:
                queue_size = self.processing_queue.qsize()
                QUEUE_SIZE.set(queue_size)
                
                if queue_size > 100:
                    self.logger.warning(f"High queue size detected: {queue_size}")
                
                await asyncio.sleep(10)
            except Exception as e:
                self.logger.error(f"Error in system monitor: {str(e)}")

    async def shutdown(self):
        """Graceful shutdown"""
        self.shutdown_event.set()
        await self.scheduler.close()
        await self.redis.close()
        await self.redis.wait_closed()

async def initialize_components():
    """Initialize system components with async support"""
    load_dotenv()
    
    logger = CustomLogger('MainApp').get_logger()
    logger.info("Initializing components...")
    
    try:
        if USE_TEST_DB:
            create_test_database()
            logger.info(f"Using test database at {TEST_DB_PATH}")
            # kb = KnowledgeBase(TEST_DB_PATH)  # Commented out
            # jira = JiraClient(TEST_DB_PATH)
            chat_memory = ChatMemory(config.CHAT_MEMORY_EXPIRATION, storage_path=TEST_DB_PATH)
            data_lineage = DataLineage(TEST_DB_PATH)
            # bias_management = BiasManagementMasterAgent(config.BIAS_THRESHOLD, storage_path=TEST_DB_PATH)
        else:
            logger.info("Using production environment")
            # kb = KnowledgeBase(config.KB_STORAGE_PATH)  # Commented out
            # jira = JiraClient()
            chat_memory = ChatMemory(config.CHAT_MEMORY_EXPIRATION)
            data_lineage = DataLineage(config.DATA_LINEAGE_STORAGE)
            # bias_management = BiasManagementMasterAgent(config.BIAS_THRESHOLD)
        
        # logger.info(kb.get_storage_info())  # Commented out
        
        llm = LLMWrapper() # (config.LLM_MODEL_NAME)
        audit_logger = AuditLogger(config.LOG_FILE_PATH)
        # access_control = AccessControl(config.ACCESS_CONTROL_CONFIG)
        # task_allocator = TaskAllocator(jira, llm, bias_management)
        
        # master_agent = MasterAgent()
        # task_allocation_agent = Agent("task_allocation", task_allocator.allocate_task)
        # master_agent.add_agent(task_allocation_agent)
        
        logger.info("All components initialized successfully.")
        
        return {
            # 'kb': kb,  # Commented out
            'llm': llm,
            # 'jira': jira,
            'logger': logger,
            'audit_logger': audit_logger,
            # 'access_control': access_control,
            'chat_memory': chat_memory,
            'data_lineage': data_lineage
            # 'bias_management': bias_management
            # 'master_agent': master_agent,
            # 'task_allocator': task_allocator
        }
    except Exception as e:
        # logger.error(f"Error initializing components: {str(e)}")
        raise ApplicationError(f"Failed to initialize components: {str(e)}")

def register_slack_handlers(slack_bot):
    # Task Management
    # slack_bot.app.command("/allocate_task")(slack_bot.handlers.handle_bias_aware_task_allocation)
    # slack_bot.app.command("/workload_report")(slack_bot.handlers.handle_workload_report)
    # slack_bot.app.command("/reallocate_tasks")(slack_bot.handlers.handle_task_reallocation)
    # slack_bot.app.command("/analyze_task")(slack_bot.handlers.handle_task_analysis)
    # slack_bot.app.command("/match_task")(slack_bot.handlers.handle_task_matching)
    # slack_bot.app.command("/recent_activities")(slack_bot.handlers.handle_recent_activities)
    
    # Knowledge Base (commented out)
    # slack_bot.app.command("/kb_add")(slack_bot.handlers.handle_kb_add)
    # slack_bot.app.command("/kb_search")(slack_bot.handlers.handle_kb_search)
    # slack_bot.app.command("/kb_update")(slack_bot.handlers.handle_kb_update)
    # slack_bot.app.command("/kb_delete")(slack_bot.handlers.handle_kb_delete)
    # slack_bot.app.command("/kb_info")(slack_bot.handlers.handle_kb_info)
    
    # # LLM functionalities
    # slack_bot.app.command("/summarize")(slack_bot.handlers.handle_summarize)
    # slack_bot.app.command("/semantic_search")(slack_bot.handlers.handle_semantic_search)
    
    # # Project Management
    # slack_bot.app.command("/sprint_planning")(slack_bot.handlers.handle_sprint_planning)
    # slack_bot.app.command("/progress_report")(slack_bot.handlers.handle_progress_report)
    # slack_bot.app.command("/bug_report")(slack_bot.handlers.handle_bug_report)
    # slack_bot.app.command("/feature_request")(slack_bot.handlers.handle_feature_request)
    # slack_bot.app.command("/code_review")(slack_bot.handlers.handle_code_review)
    # slack_bot.app.command("/ci_cd_status")(slack_bot.handlers.handle_ci_cd_status)
    # slack_bot.app.command("/retrospective")(slack_bot.handlers.handle_retrospective)
    # slack_bot.app.command("/release_planning")(slack_bot.handlers.handle_release_planning)

    # New monitoring handlers
    # slack_bot.app.command("/monitor_slack")(slack_bot.handlers.handle_monitor_slack)
    # slack_bot.app.command("/monitor_jira")(slack_bot.handlers.handle_monitor_jira)
    pass

def main():
    # try:
        components = initialize_components()
        logger = components['logger']
        # logger.info(components)
        
        slack_bot = SlackBot(components, config.SLACK_BOT_TOKEN, config.SLACK_SIGNING_SECRET)
        
        # register_slack_handlers(slack_bot)
        
        # logger.info("Starting Slack bot...")
        slack_bot.start()
    # except ApplicationError as ae:
    #     logger.error(f"Application error: {str(ae)}")
    #     # Perform any necessary cleanup or notification
    # except Exception as e:
    #     logger.error(f"Unexpected error: {str(e)}")
    #     # Perform any necessary cleanup or notification
    # finally:
    #     try:
    #         # Ensure knowledge base data is persisted when the application exits
    #         # components['kb'].persist()  # Commented out
    #         logger.info("Application shutting down.")
    #     except Exception as e:
    #         logger.error(f"Error during shutdown: {str(e)}")

if __name__ == "__main__":
    app = asyncio.run(main())
    web.run_app(app, port=8080)
