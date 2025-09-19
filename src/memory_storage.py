import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class InMemoryChatStorage:
    """In-memory conversation storage manager (fallback when Redis is unavailable)"""
    
    def __init__(self):
        """Initialize in-memory storage"""
        self.conversations = {}  # conversation_id -> conversation_data
        self.conversation_meta = {}  # conversation_id -> metadata
        self.max_history_exchanges = int(os.getenv("BOT_MAX_HISTORY_EXCHANGES", 5))
        logger.info("Initialized in-memory chat storage")
    
    def create_conversation(self, topic: str, stance: str) -> str:
        """Create a new conversation with topic and stance"""
        conversation_id = str(uuid.uuid4())
        
        conversation_meta = {
            "conversation_id": conversation_id,
            "topic": topic,
            "stance": stance,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "message_count": 0
        }
        
        self.conversation_meta[conversation_id] = conversation_meta
        self.conversations[conversation_id] = []
        
        logger.info(f"Created conversation {conversation_id} with topic: {topic}, stance: {stance}")
        return conversation_id
    
    def save_message(self, conversation_id: str, message: str, is_user: bool = True) -> bool:
        """Save a message to the conversation"""
        if conversation_id not in self.conversations:
            logger.warning(f"Conversation {conversation_id} not found")
            return False
        
        message_data = {
            "message": message,
            "is_user": is_user,
            "timestamp": datetime.now().isoformat()
        }
        
        self.conversations[conversation_id].append(message_data)
        
        # Update metadata
        if conversation_id in self.conversation_meta:
            self.conversation_meta[conversation_id]["message_count"] += 1
            self.conversation_meta[conversation_id]["updated_at"] = datetime.now().isoformat()
        
        logger.info(f"Saved message to conversation {conversation_id}")
        return True
    
    def get_conversation_history(self, conversation_id: str) -> Optional[List[Dict]]:
        """Get complete conversation history"""
        if conversation_id not in self.conversations:
            logger.warning(f"Conversation {conversation_id} not found")
            return None
        
        return self.conversations[conversation_id]
    
    def get_conversation_history_limited(self, conversation_id: str) -> Optional[List[Dict]]:
        """Get limited conversation history for API response"""
        history = self.get_conversation_history(conversation_id)
        if history is None:
            return None
        
        # Return last N exchanges (user + bot pairs)
        max_messages = self.max_history_exchanges * 2  # user + bot pairs
        return history[-max_messages:] if len(history) > max_messages else history
    
    def get_conversation_meta(self, conversation_id: str) -> Optional[Dict]:
        """Get conversation metadata"""
        return self.conversation_meta.get(conversation_id)
    
    def conversation_exists(self, conversation_id: str) -> bool:
        """Check if conversation exists"""
        return conversation_id in self.conversations
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        if conversation_id not in self.conversations:
            return False
        
        del self.conversations[conversation_id]
        if conversation_id in self.conversation_meta:
            del self.conversation_meta[conversation_id]
        
        logger.info(f"Deleted conversation {conversation_id}")
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        total_conversations = len(self.conversations)
        total_messages = sum(len(messages) for messages in self.conversations.values())
        
        return {
            "storage_type": "in_memory",
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "max_history_exchanges": self.max_history_exchanges,
            "status": "active"
        }
    
    def cleanup_expired_conversations(self):
        """Cleanup expired conversations (not applicable for in-memory storage)"""
        # In-memory storage doesn't need cleanup as it's temporary
        logger.info("In-memory storage cleanup completed (no action needed)")
