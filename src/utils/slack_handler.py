"""
Slack Handler module for managing thread-aware conversations and context preservation.
"""
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
from .logger import AuditLogger

@dataclass
class ThreadContext:
    """Data class to store thread context information"""
    thread_id: str
    channel_id: str
    user_id: str
    start_time: datetime
    last_update: datetime
    messages: List[Dict]
    metadata: Dict

class SlackHandler:
    """Handles Slack interactions with thread awareness and context preservation"""
    
    def __init__(self):
        self.active_threads: Dict[str, ThreadContext] = {}
        self.audit_logger = AuditLogger()
        
    def start_thread(self, thread_id: str, channel_id: str, user_id: str) -> ThreadContext:
        """Initialize a new thread context"""
        now = datetime.utcnow()
        context = ThreadContext(
            thread_id=thread_id,
            channel_id=channel_id,
            user_id=user_id,
            start_time=now,
            last_update=now,
            messages=[],
            metadata={}
        )
        self.active_threads[thread_id] = context
        
        # Log thread creation
        self.audit_logger.log_thread_event(
            "thread_created",
            thread_id,
            {
                "user_id": user_id,
                "channel_id": channel_id,
                "timestamp": now.isoformat()
            }
        )
        
        return context
    
    def add_message(self, thread_id: str, message: Dict) -> None:
        """Add a message to the thread context"""
        if thread_id not in self.active_threads:
            self.audit_logger.log_security_event(
                "invalid_thread_access",
                message.get("user_id"),
                {"thread_id": thread_id, "action": "add_message"}
            )
            raise ValueError(f"Thread {thread_id} not found")
            
        context = self.active_threads[thread_id]
        context.messages.append(message)
        context.last_update = datetime.utcnow()
        
        # Log message addition
        self.audit_logger.log_thread_event(
            "message_added",
            thread_id,
            {
                "user_id": context.user_id,
                "message_id": message.get("id"),
                "timestamp": context.last_update.isoformat()
            }
        )
    
    def get_thread_context(self, thread_id: str) -> Optional[ThreadContext]:
        """Retrieve thread context if it exists"""
        context = self.active_threads.get(thread_id)
        if context is None:
            self.audit_logger.log_thread_event(
                "thread_not_found",
                thread_id,
                {"action": "get_context"}
            )
        return context
    
    def update_metadata(self, thread_id: str, metadata: Dict) -> None:
        """Update thread metadata"""
        if thread_id not in self.active_threads:
            self.audit_logger.log_security_event(
                "invalid_thread_access",
                None,  # No user_id available in this context
                {"thread_id": thread_id, "action": "update_metadata"}
            )
            raise ValueError(f"Thread {thread_id} not found")
            
        context = self.active_threads[thread_id]
        context.metadata.update(metadata)
        context.last_update = datetime.utcnow()
        
        # Log metadata update
        self.audit_logger.log_thread_event(
            "metadata_updated",
            thread_id,
            {
                "user_id": context.user_id,
                "updated_fields": list(metadata.keys()),
                "timestamp": context.last_update.isoformat()
            }
        )
    
    def close_thread(self, thread_id: str) -> None:
        """Close and archive a thread"""
        if thread_id not in self.active_threads:
            self.audit_logger.log_security_event(
                "invalid_thread_access",
                None,  # No user_id available in this context
                {"thread_id": thread_id, "action": "close_thread"}
            )
            raise ValueError(f"Thread {thread_id} not found")
            
        context = self.active_threads[thread_id]
        
        # Log thread closure
        self.audit_logger.log_thread_event(
            "thread_closed",
            thread_id,
            {
                "user_id": context.user_id,
                "channel_id": context.channel_id,
                "duration": (datetime.utcnow() - context.start_time).total_seconds(),
                "message_count": len(context.messages),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Remove thread from active threads
        del self.active_threads[thread_id]
    
    def get_thread_history(self, thread_id: str) -> List[Dict]:
        """Get the message history for a thread"""
        if thread_id not in self.active_threads:
            self.audit_logger.log_security_event(
                "invalid_thread_access",
                None,  # No user_id available in this context
                {"thread_id": thread_id, "action": "get_history"}
            )
            raise ValueError(f"Thread {thread_id} not found")
            
        return self.active_threads[thread_id].messages
    
    def cleanup_inactive_threads(self, max_age_hours: int = 24) -> None:
        """Clean up inactive threads older than specified hours"""
        now = datetime.utcnow()
        threads_to_close = [
            thread_id for thread_id, context in self.active_threads.items()
            if (now - context.last_update).total_seconds() > max_age_hours * 3600
        ]
        
        for thread_id in threads_to_close:
            self.audit_logger.log_thread_event(
                "thread_auto_closed",
                thread_id,
                {
                    "reason": "inactivity",
                    "max_age_hours": max_age_hours,
                    "timestamp": now.isoformat()
                }
            )
            self.close_thread(thread_id)
