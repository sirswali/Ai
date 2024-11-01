"""
Enhanced logging module with advanced capabilities for learning and security.
"""
import os
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class UserProfile:
    """Store user-specific information and preferences"""
    user_id: str
    role: str
    preferences: Dict[str, Any]
    interaction_history: List[Dict[str, Any]]
    feedback_score: float = 0.0

class RoleManager:
    """Manage role-based access and permissions"""
    def __init__(self):
        self.role_permissions = {
            'admin': {'read', 'write', 'delete', 'manage_users'},
            'moderator': {'read', 'write', 'delete'},
            'user': {'read', 'write'},
            'viewer': {'read'}
        }
        
    def has_permission(self, role: str, permission: str) -> bool:
        """Check if role has specific permission"""
        return permission in self.role_permissions.get(role, set())

class LearningAuditLogger:
    """Enhanced logger with learning capabilities and advanced audit features"""
    
    def __init__(self, base_log_dir: str = 'logs'):
        self.base_log_dir = base_log_dir
        self.user_profiles: Dict[str, UserProfile] = {}
        self.role_manager = RoleManager()
        self.interaction_patterns = defaultdict(int)
        self.setup_loggers()
        
    def setup_loggers(self) -> None:
        """Set up various specialized loggers"""
        # Create log directories
        for log_type in ['audit', 'security', 'learning', 'performance']:
            os.makedirs(os.path.join(self.base_log_dir, log_type), exist_ok=True)
        
        # Setup specialized loggers
        self.audit_logger = self._create_logger('audit', 'audit.log')
        self.security_logger = self._create_logger('security', 'security.log')
        self.learning_logger = self._create_logger('learning', 'learning.log')
        self.performance_logger = self._create_logger('performance', 'performance.log')
    
    def _create_logger(self, name: str, filename: str) -> logging.Logger:
        """Create a specialized logger with rotating file handler"""
        logger = logging.getLogger(f'enhanced.{name}')
        logger.setLevel(logging.INFO)
        
        handler = RotatingFileHandler(
            os.path.join(self.base_log_dir, name, filename),
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def register_user(self, user_id: str, role: str, preferences: Optional[Dict] = None) -> None:
        """Register a new user with role and preferences"""
        self.user_profiles[user_id] = UserProfile(
            user_id=user_id,
            role=role,
            preferences=preferences or {},
            interaction_history=[]
        )
        
        self.security_logger.info(
            f"User registered - ID: {user_id}, Role: {role}",
            extra={'event_type': 'user_registration'}
        )
    
    def log_interaction(self, user_id: str, action: str, details: Dict[str, Any]) -> None:
        """Log user interaction with learning capabilities"""
        if user_id not in self.user_profiles:
            self.security_logger.warning(f"Unknown user interaction - ID: {user_id}")
            return
            
        profile = self.user_profiles[user_id]
        
        # Record interaction
        interaction = {
            'timestamp': datetime.utcnow().isoformat(),
            'action': action,
            'details': details
        }
        profile.interaction_history.append(interaction)
        
        # Update interaction patterns
        pattern_key = f"{action}:{details.get('context', 'unknown')}"
        self.interaction_patterns[pattern_key] += 1
        
        # Log with context
        self.learning_logger.info(
            json.dumps({
                'user_id': user_id,
                'role': profile.role,
                'action': action,
                'details': details,
                'pattern_count': self.interaction_patterns[pattern_key]
            })
        )
    
    def log_feedback(self, user_id: str, interaction_id: str, score: float, comments: Optional[str] = None) -> None:
        """Log user feedback and update learning metrics"""
        if user_id not in self.user_profiles:
            self.security_logger.warning(f"Unknown user feedback - ID: {user_id}")
            return
            
        profile = self.user_profiles[user_id]
        
        # Update user's feedback score (weighted average)
        profile.feedback_score = (profile.feedback_score * 0.8) + (score * 0.2)
        
        # Log feedback
        self.learning_logger.info(
            json.dumps({
                'user_id': user_id,
                'interaction_id': interaction_id,
                'score': score,
                'comments': comments,
                'new_feedback_score': profile.feedback_score
            })
        )
    
    def log_security_event(self, event_type: str, user_id: Optional[str], details: Dict[str, Any]) -> None:
        """Enhanced security event logging with role context"""
        event_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'details': details
        }
        
        if user_id and user_id in self.user_profiles:
            event_data['role'] = self.user_profiles[user_id].role
        
        self.security_logger.warning(json.dumps(event_data))
        
        # Log high-severity events to audit as well
        if details.get('severity') == 'high':
            self.audit_logger.error(json.dumps(event_data))
    
    def check_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission"""
        if user_id not in self.user_profiles:
            return False
        
        profile = self.user_profiles[user_id]
        has_permission = self.role_manager.has_permission(profile.role, permission)
        
        # Log permission check
        self.security_logger.info(
            json.dumps({
                'event_type': 'permission_check',
                'user_id': user_id,
                'role': profile.role,
                'permission': permission,
                'granted': has_permission
            })
        )
        
        return has_permission
    
    def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights about user behavior and preferences"""
        if user_id not in self.user_profiles:
            return {}
            
        profile = self.user_profiles[user_id]
        
        # Analyze interaction patterns
        interaction_counts = defaultdict(int)
        for interaction in profile.interaction_history:
            interaction_counts[interaction['action']] += 1
        
        return {
            'role': profile.role,
            'feedback_score': profile.feedback_score,
            'interaction_patterns': dict(interaction_counts),
            'preferences': profile.preferences
        }
    
    def log_performance_metric(self, metric_name: str, value: float, context: Dict[str, Any]) -> None:
        """Log performance metrics"""
        self.performance_logger.info(
            json.dumps({
                'timestamp': datetime.utcnow().isoformat(),
                'metric': metric_name,
                'value': value,
                'context': context
            })
        )

# Usage example
if __name__ == "__main__":
    logger = LearningAuditLogger()
    
    # Register a user
    logger.register_user("user123", "moderator", {"theme": "dark"})
    
    # Log some interactions
    logger.log_interaction(
        "user123",
        "query",
        {"context": "weather", "query": "What's the weather?"}
    )
    
    # Log feedback
    logger.log_feedback("user123", "interaction_1", 0.9, "Very helpful response")
    
    # Check permissions
    can_write = logger.check_permission("user123", "write")
    
    # Get user insights
    insights = logger.get_user_insights("user123")
    
    # Log performance
    logger.log_performance_metric("response_time", 0.23, {"query_type": "weather"})
