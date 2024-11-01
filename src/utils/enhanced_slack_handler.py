"""
Enhanced Slack Handler with advanced learning capabilities and security features.
"""
from typing import Dict, Optional, List, Any
from dataclasses import dataclass
from datetime import datetime
import time
from .enhanced_logger import LearningAuditLogger

@dataclass
class ThreadContext:
    """Enhanced thread context with learning capabilities"""
    thread_id: str
    channel_id: str
    user_id: str
    start_time: datetime
    last_update: datetime
    messages: List[Dict]
    metadata: Dict
    interaction_score: float = 0.0
    response_times: List[float] = None
    
    def __post_init__(self):
        self.response_times = self.response_times or []

class EnhancedSlackHandler:
    """Enhanced Slack handler with learning capabilities and advanced security"""
    
    def __init__(self):
        self.active_threads: Dict[str, ThreadContext] = {}
        self.logger = LearningAuditLogger()
        self.required_permissions = {
            'start_thread': 'write',
            'add_message': 'write',
            'update_metadata': 'write',
            'close_thread': 'write',
            'view_history': 'read',
            'cleanup_threads': 'manage_users'
        }
    
    def _check_permission(self, user_id: str, action: str) -> bool:
        """Check if user has permission for the action"""
        required_permission = self.required_permissions.get(action)
        if not required_permission:
            return True
        
        has_permission = self.logger.check_permission(user_id, required_permission)
        if not has_permission:
            self.logger.log_security_event(
                'permission_denied',
                user_id,
                {
                    'action': action,
                    'required_permission': required_permission,
                    'severity': 'medium'
                }
            )
        return has_permission
    
    def start_thread(self, thread_id: str, channel_id: str, user_id: str) -> ThreadContext:
        """Initialize a new thread context with enhanced tracking"""
        if not self._check_permission(user_id, 'start_thread'):
            raise PermissionError(f"User {user_id} does not have permission to start threads")
        
        start_time = time.time()
        now = datetime.utcnow()
        
        context = ThreadContext(
            thread_id=thread_id,
            channel_id=channel_id,
            user_id=user_id,
            start_time=now,
            last_update=now,
            messages=[],
            metadata={},
            interaction_score=0.0
        )
        self.active_threads[thread_id] = context
        
        # Log thread creation with performance metric
        self.logger.log_interaction(
            user_id,
            'thread_created',
            {
                'thread_id': thread_id,
                'channel_id': channel_id,
                'context': 'thread_management'
            }
        )
        
        self.logger.log_performance_metric(
            'thread_creation_time',
            time.time() - start_time,
            {'thread_id': thread_id}
        )
        
        return context
    
    def add_message(self, thread_id: str, message: Dict) -> None:
        """Add a message with enhanced tracking and learning"""
        user_id = message.get('user_id')
        if not self._check_permission(user_id, 'add_message'):
            raise PermissionError(f"User {user_id} does not have permission to add messages")
        
        start_time = time.time()
        
        if thread_id not in self.active_threads:
            self.logger.log_security_event(
                'invalid_thread_access',
                user_id,
                {
                    'thread_id': thread_id,
                    'action': 'add_message',
                    'severity': 'high'
                }
            )
            raise ValueError(f"Thread {thread_id} not found")
        
        context = self.active_threads[thread_id]
        context.messages.append(message)
        context.last_update = datetime.utcnow()
        
        # Track response time
        processing_time = time.time() - start_time
        context.response_times.append(processing_time)
        
        # Log interaction with performance metrics
        self.logger.log_interaction(
            user_id,
            'message_added',
            {
                'thread_id': thread_id,
                'message_type': message.get('type', 'unknown'),
                'context': 'message_handling'
            }
        )
        
        self.logger.log_performance_metric(
            'message_processing_time',
            processing_time,
            {
                'thread_id': thread_id,
                'message_type': message.get('type', 'unknown')
            }
        )
    
    def update_thread_score(self, thread_id: str, score: float, feedback: Optional[str] = None) -> None:
        """Update thread interaction score based on feedback"""
        if thread_id not in self.active_threads:
            raise ValueError(f"Thread {thread_id} not found")
        
        context = self.active_threads[thread_id]
        context.interaction_score = (context.interaction_score * 0.7) + (score * 0.3)
        
        self.logger.log_feedback(
            context.user_id,
            thread_id,
            score,
            feedback
        )
    
    def get_thread_insights(self, thread_id: str) -> Dict[str, Any]:
        """Get insights about thread performance and interaction patterns"""
        if thread_id not in self.active_threads:
            raise ValueError(f"Thread {thread_id} not found")
        
        context = self.active_threads[thread_id]
        
        # Calculate metrics
        avg_response_time = sum(context.response_times) / len(context.response_times) if context.response_times else 0
        message_count = len(context.messages)
        thread_duration = (datetime.utcnow() - context.start_time).total_seconds()
        
        return {
            'thread_id': thread_id,
            'interaction_score': context.interaction_score,
            'average_response_time': avg_response_time,
            'message_count': message_count,
            'thread_duration': thread_duration,
            'user_insights': self.logger.get_user_insights(context.user_id)
        }
    
    def close_thread(self, thread_id: str, user_id: str) -> None:
        """Close thread with final metrics and insights"""
        if not self._check_permission(user_id, 'close_thread'):
            raise PermissionError(f"User {user_id} does not have permission to close threads")
        
        if thread_id not in self.active_threads:
            self.logger.log_security_event(
                'invalid_thread_access',
                user_id,
                {
                    'thread_id': thread_id,
                    'action': 'close_thread',
                    'severity': 'medium'
                }
            )
            raise ValueError(f"Thread {thread_id} not found")
        
        context = self.active_threads[thread_id]
        insights = self.get_thread_insights(thread_id)
        
        # Log final thread metrics
        self.logger.log_interaction(
            user_id,
            'thread_closed',
            {
                'thread_id': thread_id,
                'metrics': insights,
                'context': 'thread_management'
            }
        )
        
        del self.active_threads[thread_id]
    
    def cleanup_inactive_threads(self, max_age_hours: int = 24, user_id: str = None) -> None:
        """Clean up inactive threads with security checks"""
        if not self._check_permission(user_id, 'cleanup_threads'):
            raise PermissionError(f"User {user_id} does not have permission to cleanup threads")
        
        now = datetime.utcnow()
        threads_to_close = [
            thread_id for thread_id, context in self.active_threads.items()
            if (now - context.last_update).total_seconds() > max_age_hours * 3600
        ]
        
        for thread_id in threads_to_close:
            try:
                self.close_thread(thread_id, user_id)
            except Exception as e:
                self.logger.log_error_event(
                    'thread_cleanup_failed',
                    {
                        'thread_id': thread_id,
                        'error': str(e),
                        'severity': 'medium'
                    },
                    user_id
                )

# Usage example
if __name__ == "__main__":
    handler = EnhancedSlackHandler()
    
    # Register a test user
    handler.logger.register_user("user123", "moderator", {"theme": "dark"})
    
    # Start a thread
    context = handler.start_thread("thread123", "channel456", "user123")
    
    # Add some messages
    handler.add_message("thread123", {
        "user_id": "user123",
        "type": "text",
        "content": "Hello!",
        "id": "msg1"
    })
    
    # Update thread score
    handler.update_thread_score("thread123", 0.9, "Great interaction!")
    
    # Get insights
    insights = handler.get_thread_insights("thread123")
    
    # Close thread
    handler.close_thread("thread123", "user123")
