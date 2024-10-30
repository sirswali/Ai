# Add these imports at the top with other imports
import asyncio
import aiojobs
import redis
import time
from typing import Optional
from redis.exceptions import ConnectionError as RedisConnectionError

# Add this helper class before AsyncProcessingSystem
class MemoryCache:
    """Fallback in-memory cache when Redis is unavailable"""
    def __init__(self):
        self._cache = {}
        self._lock = asyncio.Lock()
    
    async def set(self, key: str, value: str, ex: int = None):
        async with self._lock:
            self._cache[key] = {
                'value': value,
                'expires_at': time.time() + ex if ex else None
            }
    
    async def get(self, key: str) -> Optional[str]:
        async with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if entry['expires_at'] is None or time.time() < entry['expires_at']:
                    return entry['value']
                else:
                    del self._cache[key]
            return None
    
    async def ping(self):
        return True
    
    async def close(self):
        async with self._lock:
            self._cache.clear()

async def initialize_components():
    """Initialize system components"""
    from utils.logging.logger import setup_logger
    from task_management.allocator import TaskAllocator
    from knowledge_base.kb import KnowledgeBase
    from llm.wrapper import LLMWrapper
    
    components = {
        'logger': setup_logger(),
        'task_allocator': TaskAllocator(),
        'kb': KnowledgeBase(),
        'llm': LLMWrapper()
    }
    
    return components

# Modify AsyncProcessingSystem.__init__ to include fallback
class AsyncProcessingSystem:
    def __init__(self, components, redis_url: str = "redis://localhost", max_queue_size: int = 1000):
        self.components = components
        self.processing_queue = asyncio.Queue(maxsize=max_queue_size)
        self.scheduler = aiojobs.Scheduler()
        self.shutdown_event = asyncio.Event()
        self.circuit_breaker = MultiAgentCircuitBreaker()
        self.config = MultiAgentConfig()
        self.logger = components['logger']
        self.input_module = InputModule()

        # Try to connect to Redis with fallback to memory cache
        try:
            self.redis = redis.from_url(redis_url, decode_responses=True)
            self.logger.info("Successfully connected to Redis")
        except Exception as e:
            self.logger.warning(
                f"Redis connection failed ({str(e)}). Falling back to in-memory storage. "
                "To use Redis, please install and start Redis server:\n"
                "Windows: https://github.com/microsoftarchive/redis/releases\n"
                "Linux: sudo apt-get install redis-server\n"
                "Mac: brew install redis"
            )
            self.redis = MemoryCache()

async def main():
    """Main entry point"""
    components = await initialize_components()
    app = AsyncProcessingSystem(components)
    return app

if __name__ == "__main__":
    app = asyncio.run(main())
