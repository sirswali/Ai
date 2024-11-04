import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check required environment variables
required_env_vars = ['ALLOWED_USERS', 'ENCRYPTION_KEY']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    logger.warning(f"The following required environment variables are not set: {', '.join(missing_vars)}")

# Set default values for optional environment variables
os.environ.setdefault('JIRA_SERVER', 'http://localhost:8080')
os.environ.setdefault('JIRA_USERNAME', 'default_user')
os.environ.setdefault('JIRA_PASSWORD', 'default_pass')
os.environ.setdefault('JIRA_PROJECT_KEY', 'TEST')
os.environ.setdefault('LLM_MODEL_NAME', 'EleutherAI/gpt-neo-1.3B')

async def initialize_components() -> Dict[str, Any]:
    """Initialize all system components"""
    try:
        # Add the src directory to Python path to fix relative imports
        import sys
        from pathlib import Path
        src_path = str(Path(__file__).parent.parent)
        if src_path not in sys.path:
            sys.path.append(src_path)

        # Initialize JIRA client in test mode
        from jira.client import JiraClient
        jira_client = JiraClient(db_path=":memory:")  # Use in-memory SQLite for testing
        
        # Initialize LLM wrapper
        from llm.wrapper import LLMWrapper
        llm = LLMWrapper()
        
        # Initialize task allocator with dependencies
        from task_management.allocator import TaskAllocator
        task_allocator = TaskAllocator(jira_client=jira_client, llm=llm)
        
        # Initialize other components as needed
        components = {
            'jira_client': jira_client,
            'llm': llm,
            'task_allocator': task_allocator
        }
        
        return components
        
    except ImportError as e:
        logger.warning(f"Error importing required components: {str(e)}. Make sure Jira and LLM modules are properly set up.")
        return {}
    except Exception as e:
        logger.error(f"Error initializing components: {str(e)}")
        return {}

async def run_application(components: Dict[str, Any]):
    """Run the main application loop"""
    try:
        while True:
            # Your application logic here
            await asyncio.sleep(1)  # Prevent CPU spinning
    except Exception as e:
        logger.error(f"Error in application loop: {str(e)}")

async def main():
    """Main application entry point"""
    try:
        # Initialize components
        components = await initialize_components()
        if not components:
            logger.error("Failed to initialize components. Exiting...")
            return None
            
        logger.info("Components initialized successfully")
        
        # Run the application
        await run_application(components)
        
    except Exception as e:
        logger.error(f"Error in main application: {str(e)}")
        return None

if __name__ == "__main__":
    try:
        # Create and set the event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the application
        loop.run_until_complete(main())
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application startup error: {str(e)}")
    finally:
        # Clean up
        try:
            loop.close()
        except Exception:
            pass
