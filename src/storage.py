import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import redis

logger = logging.getLogger(__name__)

class ChatStorage:
    """Redis-based conversation storage manager"""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, password: str = None):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {host}:{port}")
        except redis.ConnectionError as e:
            logger.error(f"Error connecting to Redis: {e}")
            raise
        
        self.max_history_exchanges = int(os.getenv("BOT_MAX_HISTORY_EXCHANGES", 5))
    
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
        
        try:
            self.redis_client.setex(
                f"conversation_meta:{conversation_id}",
                7 * 24 * 3600,
                json.dumps(conversation_meta)
            )
            
            self.redis_client.setex(
                f"conversation_messages:{conversation_id}",
                7 * 24 * 3600,
                json.dumps([])
            )
            
            logger.info(f"New conversation created: {conversation_id} - Topic: {topic}, Stance: {stance}")
            return conversation_id
            
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            raise
    
    def get_conversation_meta(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation metadata"""
        try:
            meta_data = self.redis_client.get(f"conversation_meta:{conversation_id}")
            if meta_data:
                return json.loads(meta_data)
            return None
        except Exception as e:
            logger.error(f"Error getting conversation metadata {conversation_id}: {e}")
            return None
    
    def get_conversation_topic_and_stance(self, conversation_id: str) -> Optional[Dict[str, str]]:
        """Get conversation topic and stance"""
        try:
            meta = self.get_conversation_meta(conversation_id)
            if meta:
                return {
                    "topic": meta["topic"],
                    "stance": meta["stance"]
                }
            return None
        except Exception as e:
            logger.error(f"Error getting topic and stance for conversation {conversation_id}: {e}")
            return None
    
    def save_message(self, conversation_id: str, message: str, is_user: bool = True) -> bool:
        """Save a message to an existing conversation"""
        try:
            meta = self.get_conversation_meta(conversation_id)
            if not meta:
                logger.warning(f"Conversation {conversation_id} not found")
                return False
            
            chat_message = {
                "id": str(uuid.uuid4()),
                "message": message,
                "is_user": is_user,
                "timestamp": datetime.now().isoformat()
            }
            
            messages_key = f"conversation_messages:{conversation_id}"
            existing_messages = self.redis_client.get(messages_key)
            
            if existing_messages:
                messages = json.loads(existing_messages)
            else:
                messages = []
            
            messages.append(chat_message)
            
            self.redis_client.setex(
                messages_key,
                7 * 24 * 3600,
                json.dumps(messages)
            )
            
            meta["message_count"] = len(messages)
            meta["updated_at"] = datetime.now().isoformat()
            
            self.redis_client.setex(
                f"conversation_meta:{conversation_id}",
                7 * 24 * 3600,
                json.dumps(meta)
            )
            
            logger.info(f"Message saved in conversation {conversation_id}: {len(messages)} total messages")
            return True
            
        except Exception as e:
            logger.error(f"Error saving message in conversation {conversation_id}: {e}")
            return False
    
    def get_conversation_history(self, conversation_id: str, limit: int = None) -> Optional[List[Dict[str, Any]]]:
        """Get conversation history with optional limit"""
        try:
            messages_key = f"conversation_messages:{conversation_id}"
            messages_data = self.redis_client.get(messages_key)
            
            if not messages_data:
                return None
            
            messages = json.loads(messages_data)
            
            if limit and len(messages) > limit:
                messages = messages[-limit:]
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting conversation history {conversation_id}: {e}")
            return None
    
    def get_conversation_history_limited(self, conversation_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get limited history (last N per side, maximum 2N)"""
        try:
            messages = self.get_conversation_history(conversation_id)
            if not messages:
                return None
            
            user_messages = [msg for msg in messages if msg["is_user"]]
            bot_messages = [msg for msg in messages if not msg["is_user"]]
            
            max_exchanges = self.max_history_exchanges
            recent_user_messages = user_messages[-max_exchanges:] if len(user_messages) > max_exchanges else user_messages
            recent_bot_messages = bot_messages[-max_exchanges:] if len(bot_messages) > max_exchanges else bot_messages
            
            all_recent_messages = []
            for msg in recent_user_messages:
                all_recent_messages.append((msg["timestamp"], "user", msg["message"]))
            for msg in recent_bot_messages:
                all_recent_messages.append((msg["timestamp"], "bot", msg["message"]))
            
            all_recent_messages.sort(key=lambda x: x[0])
            
            formatted_messages = []
            for timestamp, role, message in all_recent_messages:
                formatted_messages.append({
                    "role": role,
                    "message": message
                })
            
            return formatted_messages
            
        except Exception as e:
            logger.error(f"Error getting limited history for conversation {conversation_id}: {e}")
            return None
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a complete conversation"""
        try:
            meta_deleted = self.redis_client.delete(f"conversation_meta:{conversation_id}")
            messages_deleted = self.redis_client.delete(f"conversation_messages:{conversation_id}")
            
            if meta_deleted or messages_deleted:
                logger.info(f"Conversation {conversation_id} deleted successfully")
                return True
            else:
                logger.warning(f"Conversation {conversation_id} not found for deletion")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting conversation {conversation_id}: {e}")
            return False
    
    def conversation_exists(self, conversation_id: str) -> bool:
        """Check if a conversation exists"""
        try:
            meta = self.redis_client.get(f"conversation_meta:{conversation_id}")
            return meta is not None
        except Exception as e:
            logger.error(f"Error checking conversation existence {conversation_id}: {e}")
            return False
    
    def get_all_conversations(self) -> List[Dict[str, Any]]:
        """Get all active conversations"""
        try:
            conversations = []
            pattern = "conversation_meta:*"
            
            for key in self.redis_client.scan_iter(match=pattern):
                conversation_id = key.replace("conversation_meta:", "")
                meta = self.get_conversation_meta(conversation_id)
                if meta:
                    conversations.append(meta)
            
            return conversations
            
        except Exception as e:
            logger.error(f"Error getting all conversations: {e}")
            return []
    
    def cleanup_expired_conversations(self) -> int:
        """Clean up expired conversations (Redis handles this automatically with TTL)"""
        try:
            return 0
        except Exception as e:
            logger.error(f"Error during conversation cleanup: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            pattern = "conversation_meta:*"
            active_conversations = len(list(self.redis_client.scan_iter(match=pattern)))
            
            conversations = self.get_all_conversations()
            total_messages = sum(conv.get("message_count", 0) for conv in conversations)
            
            return {
                "active_conversations": active_conversations,
                "total_messages": total_messages,
                "storage_type": "redis",
                "ttl_days": 7,
                "max_history_exchanges": self.max_history_exchanges,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"error": str(e)}
    
    def update_conversation_meta(self, conversation_id: str, updates: Dict[str, Any]) -> bool:
        """Update conversation metadata"""
        try:
            meta = self.get_conversation_meta(conversation_id)
            if not meta:
                return False
            
            meta.update(updates)
            meta["updated_at"] = datetime.now().isoformat()
            
            self.redis_client.setex(
                f"conversation_meta:{conversation_id}",
                7 * 24 * 3600,
                json.dumps(meta)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating conversation metadata {conversation_id}: {e}")
            return False
