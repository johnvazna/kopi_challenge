import pytest
import sys
import os
from unittest.mock import Mock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    with patch('src.storage.redis.Redis') as mock_redis_class:
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.get.return_value = None
        mock_redis_instance.setex.return_value = True
        mock_redis_instance.delete.return_value = 1
        mock_redis_instance.scan_iter.return_value = []
        mock_redis_class.return_value = mock_redis_instance
        yield mock_redis_instance

@pytest.fixture
def mock_storage(mock_redis):
    """Mock storage instance"""
    with patch('src.main.ChatStorage') as mock_storage_class:
        mock_storage_instance = Mock()
        mock_storage_instance.get_stats.return_value = {"active_conversations": 0, "total_messages": 0}
        mock_storage_instance.conversation_exists.return_value = False
        mock_storage_instance.create_conversation.return_value = "test-conversation-id"
        mock_storage_instance.save_message.return_value = True
        mock_storage_instance.get_conversation_history_limited.return_value = [
            {"role": "user", "message": "Hello"},
            {"role": "bot", "message": "Test response"}
        ]
        mock_storage_instance.get_conversation_history.return_value = [
            {"is_user": True, "message": "Hello", "timestamp": "2024-01-01T00:00:00"},
            {"is_user": False, "message": "Test response", "timestamp": "2024-01-01T00:00:01"}
        ]
        mock_storage_instance.get_conversation_meta.return_value = {
            "topic": "Test Topic",
            "stance": "Pro",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:01"
        }
        mock_storage_instance.delete_conversation.return_value = True
        
        # Track deleted conversations
        deleted_conversations = set()
        
        # Mock conversation_exists to return True for existing conversations, False for deleted ones
        def mock_conversation_exists(conv_id):
            return conv_id == "test-conversation-id" and conv_id not in deleted_conversations
        mock_storage_instance.conversation_exists.side_effect = mock_conversation_exists
        
        # Mock get_conversation_history_limited to return different responses for different calls
        call_count = [0]  # Use list to make it mutable in closure
        def mock_get_history_limited(conv_id):
            if conv_id == "test-conversation-id" and conv_id not in deleted_conversations:
                call_count[0] += 1
                if call_count[0] == 1:
                    return [
                        {"role": "user", "message": "Hello"},
                        {"role": "bot", "message": "Excellent! I have chosen to debate about: **Test Topic**\n\nMy stance is **Pro**. I am completely convinced that:\n\n1. Test reason 1\n2. Test reason 2\n\nTest analogy\n\nWhat do you think about test topic? Can you give me arguments against it?"}
                    ]
                else:
                    return [
                        {"role": "user", "message": "Hello"},
                        {"role": "bot", "message": "Excellent! I have chosen to debate about: **Test Topic**\n\nMy stance is **Pro**. I am completely convinced that:\n\n1. Test reason 1\n2. Test reason 2\n\nTest analogy\n\nWhat do you think about test topic? Can you give me arguments against it?"},
                        {"role": "user", "message": "Follow up message"},
                        {"role": "bot", "message": "Regarding your comment about **Test Topic**, my **Pro** stance remains firm.\n\nI appreciate your perspective, even though it's different from mine.\n\nMy position is clear: **Pro** on **Test Topic**.\n\n1. Test reason 1\n2. Test reason 2\n\nTest analogy\n\nTest question?"}
                    ]
            return []
        mock_storage_instance.get_conversation_history_limited.side_effect = mock_get_history_limited
        
        # Mock get_conversation_meta to return None for invalid conversations
        def mock_get_conversation_meta(conv_id):
            if conv_id == "test-conversation-id" and conv_id not in deleted_conversations:
                return {
                    "topic": "Test Topic",
                    "stance": "Pro",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:01"
                }
            return None
        mock_storage_instance.get_conversation_meta.side_effect = mock_get_conversation_meta
        
        # Mock get_conversation_history to return None for invalid conversations
        def mock_get_conversation_history(conv_id, limit=None):
            if conv_id == "test-conversation-id" and conv_id not in deleted_conversations:
                return [
                    {"is_user": True, "message": "Hello", "timestamp": "2024-01-01T00:00:00"},
                    {"is_user": False, "message": "Test response", "timestamp": "2024-01-01T00:00:01"}
                ]
            return None
        mock_storage_instance.get_conversation_history.side_effect = mock_get_conversation_history
        
        # Mock delete_conversation to actually mark conversations as deleted
        def mock_delete_conversation(conv_id):
            if conv_id == "test-conversation-id":
                deleted_conversations.add(conv_id)
                return True
            return False
        mock_storage_instance.delete_conversation.side_effect = mock_delete_conversation
        
        mock_storage_class.return_value = mock_storage_instance
        yield mock_storage_instance

@pytest.fixture
def mock_chatbot():
    """Mock chatbot instance"""
    with patch('src.main.DebateChatbot') as mock_chatbot_class:
        mock_chatbot_instance = Mock()
        mock_chatbot_instance.pick_topic_and_stance.return_value = {
            "topic": "Test Topic",
            "stance": "Pro"
        }
        mock_chatbot_instance.generate_initial_response.return_value = "Excellent! I have chosen to debate about: **Test Topic**\n\nMy stance is **Pro**. I am completely convinced that:\n\n1. Test reason 1\n2. Test reason 2\n\nTest analogy\n\nWhat do you think about test topic? Can you give me arguments against it?"
        mock_chatbot_instance.generate_reply.return_value = "Regarding your comment about **Test Topic**, my **Pro** stance remains firm.\n\nI appreciate your perspective, even though it's different from mine.\n\nMy position is clear: **Pro** on **Test Topic**.\n\n1. Test reason 1\n2. Test reason 2\n\nTest analogy\n\nTest question?"
        mock_chatbot_instance.get_topic_info.return_value = {
            "topic": "Test Topic",
            "position": "Pro",
            "reasons": ["Reason 1", "Reason 2"]
        }
        mock_chatbot_instance.get_personality_summary.return_value = "Test personality summary"
        mock_chatbot_class.return_value = mock_chatbot_instance
        yield mock_chatbot_instance

@pytest.fixture
def app_with_mocks(mock_storage, mock_chatbot):
    """App instance with mocked dependencies"""
    with patch('src.main.storage', mock_storage), \
         patch('src.main.chatbot', mock_chatbot):
        from src.main import app
        yield app

@pytest.fixture
def client_with_mocks(app_with_mocks):
    """Test client with mocked dependencies"""
    from fastapi.testclient import TestClient
    return TestClient(app_with_mocks)
