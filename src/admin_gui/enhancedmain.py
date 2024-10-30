"""Enhanced version of main.py with comprehensive fixes for identified issues"""

import asyncio
import logging
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from aiohttp import web
import aiojobs
from prometheus_client import Counter, Histogram, Gauge
import aioredis
from multi_agent import InputModule

# Metrics setup
PROCESSED_MESSAGES = Counter('processed_messages_total', 'Number of processed messages')
PROCESSING_TIME = Histogram('message_processing_seconds', 'Time spent processing messages')
QUEUE_SIZE = Gauge('processing_queue_size', 'Current size of the processing queue')
ERROR_COUNTER = Counter('processing_errors_total', 'Number of processing errors')

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

class AsyncProcessingSystem:
    def __init__(self, redis_url: str, max_queue_size: int = 1000):
        self.redis = aioredis.from_url(redis_url)
        self.processing_queue = asyncio.Queue(maxsize=max_queue_size)
        self.response_queues: Dict[str, asyncio.Queue] = {}
        self.rate_limiter = RateLimiter(rate_limit=100, time_window=60)
        self.error_handler = ErrorHandler()
        self.scheduler = aiojobs.Scheduler()
        self.worker_pool = WorkerPool(size=5)
        self.monitor = SystemMonitor()
        self.shutdown_event = asyncio.Event()
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        self.setup_logging()

    async def initialize(self):
        """Initialize system components"""
        await self.scheduler.spawn(self.monitor.start_monitoring(self))
        await self.worker_pool.start()
        await self.cleanup_scheduler.start()

    async def shutdown(self):
        """Graceful shutdown of all components"""
        self.shutdown_event.set()
        
        # Stop accepting new messages
        self.processing_queue.put_nowait(None)  # Sentinel value
        
        # Wait for ongoing processing to complete
        await self.worker_pool.shutdown(timeout=30)
        await self.scheduler.close()
        
        # Clean up Redis connections
        await self.redis.close()
        await self.redis.wait_closed()

class WorkerPool:
    """Manages a pool of worker processes"""
    
    def __init__(self, size: int = 5):
        self.size = size
        self.workers: List[asyncio.Task] = []
        self.queue = asyncio.Queue()
        self.running = True

    async def start(self):
        """Start worker processes"""
        for _ in range(self.size):
            worker = asyncio.create_task(self.worker_loop())
            self.workers.append(worker)

    async def worker_loop(self):
        """Main worker loop for processing messages"""
        while self.running:
            try:
                message = await self.queue.get()
                if message is None:  # Shutdown signal
                    break
                    
                async with PROCESSING_TIME.time():
                    await self.process_message(message)
                    
                PROCESSED_MESSAGES.inc()
                
            except Exception as e:
                ERROR_COUNTER.inc()
                await self.handle_error(e)
            finally:
                self.queue.task_done()

    async def process_message(self, message: Message):
        """Process a single message with error handling and retries"""
        try:
            async with self.rate_limiter:
                result = await asyncio.to_thread(
                    self.input_module.orchestrator.process_query,
                    message.content,
                    message.user_id
                )
                
                # Store result in Redis for fault tolerance
                await self.redis.set(
                    f"result:{message.id}",
                    result,
                    ex=3600  # 1 hour expiry
                )
                
                # Send response
                await self.send_response(message, result)
                
        except Exception as e:
            if message.retries < message.max_retries:
                await self.requeue_with_backoff(message)
            else:
                await self.handle_failed_message(message, e)

class RateLimiter:
    """Token bucket rate limiter with Redis backend"""
    
    def __init__(self, redis_client, key_prefix: str = "rate_limit",
                 rate_limit: int = 100, time_window: int = 60):
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.rate_limit = rate_limit
        self.time_window = time_window

    async def acquire(self, key: str) -> bool:
        """Attempt to acquire a rate limit token"""
        redis_key = f"{self.key_prefix}:{key}"
        
        async with self.redis.pipeline() as pipe:
            current_time = time.time()
            
            # Clean up old tokens
            await pipe.zremrangebyscore(
                redis_key,
                "-inf",/g. u
                current_time - self.time_window
            )
                        # Count current tokens
            token_count = await pipe.zcard(redis_key)
            
            if token_count < self.rate_limit:
                # Add new token
                await pipe.zadd(redis_key, {str(current_time): current_time})
                await pipe.expire(redis_key, self.time_window)
                return True
                
            return False

class SystemMonitor:
    """System monitoring and alerting"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.alert_thresholds = {
            'queue_size': 100,
            'error_rate': 0.1,
            'processing_time': 5.0
        }

    async def start_monitoring(self, system):
        """Start monitoring tasks"""
        while not system.shutdown_event.is_set():
            await self.collect_metrics(system)
            await self.check_alerts()
            await asyncio.sleep(10)

    async def collect_metrics(self, system):
        """Collect system metrics"""
        queue_size = system.processing_queue.qsize()
        QUEUE_SIZE.set(queue_size)
        
        self.metrics['queue_size'].append(queue_size)
        self.metrics['worker_count'] = len(system.worker_pool.workers)
        
        # Cleanup old metrics
        if len(self.metrics['queue_size']) > 100:
            self.metrics['queue_size'] = self.metrics['queue_size'][-100:]

    async def check_alerts(self):
        """Check for alert conditions"""
        avg_queue_size = sum(self.metrics['queue_size']) / len(self.metrics['queue_size'])
        
        if avg_queue_size > self.alert_thresholds['queue_size']:
            logging.warning(f"Queue size alert: {avg_queue_size}")
            # Implement alert notification system here

def setup_routes(app: web.Application):
    """Setup application routes"""
    app.router.add_post('/slack/events', handle_slack_event)
    app.router.add_get('/health', health_check)
    app.router.add_get('/metrics', metrics_handler)

async def handle_slack_event(request: web.Request):
    """Handle incoming Slack events"""
    system = request.app['processing_system']
    
    try:
        event_data = await request.json()
        
        # Handle Slack verification
        if event_data.get('type') == 'url_verification':
            return web.Response(text=event_data.get('challenge', ''))
            
        if 'event' in event_data:
            event = event_data['event']
            if event.get('type') == 'message' and 'bot_id' not in event:
                message = Message(
                    id=event.get('ts', str(time.time())),
                    user_id=event['user'],
                    content=event['text'],
                    channel=event['channel'],
                    timestamp=time.time()
                )
                
                await system.processing_queue.put(message)
                return web.Response(status=202)  # Accepted
                
    except Exception as e:
        logging.error(f"Error handling Slack event: {e}", exc_info=True)
        return web.Response(status=500)

async def main():
    """Application entry point"""
    # Initialize the application
    app = web.Application()
    
    # Initialize the processing system
    system = AsyncProcessingSystem(
        redis_url="redis://localhost",
        max_queue_size=1000
    )
    
    # Store system in app state
    app['processing_system'] = system
    
    # Setup routes
    setup_routes(app)
    
    # Setup startup and cleanup
    app.on_startup.append(lambda app: system.initialize())
    app.on_cleanup.append(lambda app: system.shutdown())
    
    return app

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    app = asyncio.run(main())
    web.run_app(app, port=8080)
