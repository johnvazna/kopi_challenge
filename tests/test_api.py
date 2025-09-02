import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestAPIEndpoints:
    """Tests for API endpoints"""
    
    def test_root_endpoint(self, client_with_mocks):
        """Test root endpoint"""
        response = client_with_mocks.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "description" in data
        assert "version" in data
        assert "endpoints" in data
        assert data["version"] == "1.0.0"
    
    def test_health_endpoint(self, client_with_mocks):
        """Test health check endpoint"""
        response = client_with_mocks.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert data["status"] == "healthy"
    
    def test_personality_endpoint(self, client_with_mocks):
        """Test personality endpoint"""
        response = client_with_mocks.get("/personality")
        assert response.status_code == 200
        
        data = response.json()
        assert "personality" in data
        assert "description" in data
        assert "current_topic" in data
        assert "position" in data
        assert data["personality"] == "debate-focused"
        assert len(data["current_topic"]) > 0
        assert len(data["position"]) > 0
    
    def test_chat_endpoint_new_conversation(self, client_with_mocks):
        """Test chat endpoint with new conversation"""
        chat_request = {
            "message": "Hello, what topic are we going to debate?"
        }
        
        response = client_with_mocks.post("/chat", json=chat_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "conversation_id" in data
        assert "message" in data
        assert isinstance(data["message"], list)
        assert len(data["message"]) == 2
        assert data["message"][0]["role"] == "user"
        assert data["message"][1]["role"] == "bot"
        assert len(data["conversation_id"]) > 0
    
    def test_chat_endpoint_existing_conversation(self, client_with_mocks):
        """Test chat endpoint with existing conversation"""
        chat_request = {
            "message": "Hello, let's start debating"
        }
        
        response1 = client_with_mocks.post("/chat", json=chat_request)
        assert response1.status_code == 200
        
        conversation_id = response1.json()["conversation_id"]
        
        chat_request2 = {
            "message": "Can you explain your stance better?",
            "conversation_id": conversation_id
        }
        
        response2 = client_with_mocks.post("/chat", json=chat_request2)
        assert response2.status_code == 200
        
        data2 = response2.json()
        assert data2["conversation_id"] == conversation_id
        assert len(data2["message"]) == 4
    
    def test_chat_endpoint_invalid_conversation(self, client_with_mocks):
        """Test chat endpoint with invalid conversation"""
        chat_request = {
            "message": "Hello",
            "conversation_id": "invalid-conversation-id"
        }
        
        response = client_with_mocks.post("/chat", json=chat_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "conversation_id" in data
        assert data["conversation_id"] != "invalid-conversation-id"
    
    def test_chat_endpoint_empty_message(self, client_with_mocks):
        """Test chat endpoint with empty message"""
        chat_request = {
            "message": ""
        }
    
        response = client_with_mocks.post("/chat", json=chat_request)
        assert response.status_code == 422
    
    def test_chat_endpoint_missing_message(self, client_with_mocks):
        """Test chat endpoint without message field"""
        chat_request = {}
    
        response = client_with_mocks.post("/chat", json=chat_request)
        assert response.status_code == 422
    
    def test_chat_endpoint_whitespace_message(self, client_with_mocks):
        """Test chat endpoint with whitespace-only message"""
        chat_request = {
            "message": "   "
        }
    
        response = client_with_mocks.post("/chat", json=chat_request)
        assert response.status_code == 422
    
    def test_get_chat_history_valid_conversation(self, client_with_mocks):
        """Test getting valid chat history"""
        chat_request = {
            "message": "Hello, let's start the debate"
        }
        
        chat_response = client_with_mocks.post("/chat", json=chat_request)
        conversation_id = chat_response.json()["conversation_id"]
        
        response = client_with_mocks.get(f"/chat/{conversation_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "conversation_id" in data
        assert "messages" in data
        assert "total_messages" in data
        assert "topic" in data
        assert "stance" in data
        assert data["conversation_id"] == conversation_id
        assert data["total_messages"] == 2
        assert data["topic"] is not None
        assert data["stance"] is not None
    
    def test_get_chat_history_invalid_conversation(self, client_with_mocks):
        """Test getting invalid chat history"""
        response = client_with_mocks.get("/chat/invalid-conversation-id")
        assert response.status_code == 404
    
    def test_delete_chat_conversation(self, client_with_mocks):
        """Test deleting chat conversation"""
        chat_request = {
            "message": "Hello"
        }
        
        chat_response = client_with_mocks.post("/chat", json=chat_request)
        conversation_id = chat_response.json()["conversation_id"]
        
        response = client_with_mocks.delete(f"/chat/{conversation_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert data["conversation_id"] == conversation_id
        
        history_response = client_with_mocks.get(f"/chat/{conversation_id}")
        assert history_response.status_code == 404
    
    def test_delete_chat_conversation_invalid(self, client_with_mocks):
        """Test deleting invalid chat conversation"""
        response = client_with_mocks.delete("/chat/invalid-conversation-id")
        assert response.status_code == 404
    
    def test_stats_endpoint(self, client_with_mocks):
        """Test stats endpoint"""
        response = client_with_mocks.get("/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "storage" in data
        assert "chatbot_personality" in data
        assert "api_version" in data
        assert data["chatbot_personality"] == "debate-focused"
        assert data["api_version"] == "1.0.0"

class TestChatbotResponses:
    """Tests for chatbot responses"""
    
    def test_chatbot_initial_response(self, client_with_mocks):
        """Test chatbot initial response with topic and stance"""
        chat_request = {"message": "Hello, let's start debating"}
        response = client_with_mocks.post("/chat", json=chat_request)
        assert response.status_code == 200
        
        data = response.json()
        bot_message = data["message"][1]["message"]
        
        assert "**" in bot_message
        assert "What do you think about" in bot_message
        assert "Can you give me arguments against it?" in bot_message
    
    def test_chatbot_debate_responses(self, client_with_mocks):
        """Test chatbot responses in debate"""
        chat_request = {"message": "Hello"}
        response1 = client_with_mocks.post("/chat", json=chat_request)
        conversation_id = response1.json()["conversation_id"]
        
        chat_request2 = {
            "message": "I don't agree with your stance",
            "conversation_id": conversation_id
        }
        
        response2 = client_with_mocks.post("/chat", json=chat_request2)
        assert response2.status_code == 200
        
        data2 = response2.json()
        bot_message = data2["message"][-1]["message"]
        
        assert "stance" in bot_message
        assert "unshakeable" in bot_message.lower() or "firm" in bot_message.lower()
    
    def test_chatbot_greetings(self, client_with_mocks):
        """Test chatbot responses to greetings"""
        greetings = ["Hello", "Good morning", "Hi"]
        
        for greeting in greetings:
            chat_request = {"message": greeting}
            response = client_with_mocks.post("/chat", json=chat_request)
            assert response.status_code == 200
            
            data = response.json()
            bot_message = data["message"][1]["message"]
            assert len(bot_message) > 0
            assert "**" in bot_message
    
    def test_chatbot_farewells(self, client_with_mocks):
        """Test chatbot responses to farewells"""
        chat_request = {"message": "Hello"}
        response1 = client_with_mocks.post("/chat", json=chat_request)
        conversation_id = response1.json()["conversation_id"]
        
        farewell_request = {
            "message": "Goodbye",
            "conversation_id": conversation_id
        }
        
        response2 = client_with_mocks.post("/chat", json=farewell_request)
        assert response2.status_code == 200
        
        data2 = response2.json()
        bot_message = data2["message"][-1]["message"]
        assert len(bot_message) > 0
        assert "stance" in bot_message.lower()

class TestConversationManagement:
    """Tests for conversation management"""
    
    def test_conversation_creation_with_topic_and_stance(self, client_with_mocks):
        """Test that a conversation can be started"""
        chat_request = {"message": "Hello, let's start debating"}
        response = client_with_mocks.post("/chat", json=chat_request)
        assert response.status_code == 200
        
        data = response.json()
        conversation_id = data["conversation_id"]
        
        assert len(conversation_id) > 0
        assert len(data["message"]) == 2
        
        history_response = client_with_mocks.get(f"/chat/{conversation_id}")
        assert history_response.status_code == 200
        
        history_data = history_response.json()
        assert "topic" in history_data
        assert "stance" in history_data
        assert history_data["topic"] is not None
        assert history_data["stance"] is not None
    
    def test_conversation_continuation_maintains_stance(self, client_with_mocks):
        """Test that conversation can continue and bot responds maintaining stance"""
        chat_request = {"message": "Hello"}
        response1 = client_with_mocks.post("/chat", json=chat_request)
        conversation_id = response1.json()["conversation_id"]
        
        history1 = client_with_mocks.get(f"/chat/{conversation_id}")
        initial_topic = history1.json()["topic"]
        initial_stance = history1.json()["stance"]
        
        chat_request2 = {
            "message": "Why do you believe that?",
            "conversation_id": conversation_id
        }
        
        response2 = client_with_mocks.post("/chat", json=chat_request2)
        assert response2.status_code == 200
        
        history2 = client_with_mocks.get(f"/chat/{conversation_id}")
        final_topic = history2.json()["topic"]
        final_stance = history2.json()["stance"]
        
        assert final_topic == initial_topic
        assert final_stance == initial_stance
        
        bot_message = response2.json()["message"][-1]["message"]
        assert initial_stance in bot_message
        assert initial_topic in bot_message
    
    def test_conversation_history_limit(self, client_with_mocks):
        """Test conversation history limit (last 5 per side, maximum 10)"""
        chat_request = {"message": "Hello"}
        response = client_with_mocks.post("/chat", json=chat_request)
        conversation_id = response.json()["conversation_id"]
        
        for i in range(8):
            chat_request = {
                "message": f"Message {i+1}",
                "conversation_id": conversation_id
            }
            response = client_with_mocks.post("/chat", json=chat_request)
            assert response.status_code == 200
        
        history_response = client_with_mocks.get(f"/chat/{conversation_id}")
        assert history_response.status_code == 200
        
        data = history_response.json()
        assert data["total_messages"] <= 10
    
    def test_conversation_persistence(self, client_with_mocks):
        """Test conversation persistence"""
        chat_request = {"message": "Hello"}
        response = client_with_mocks.post("/chat", json=chat_request)
        conversation_id = response.json()["conversation_id"]
        
        history_response = client_with_mocks.get(f"/chat/{conversation_id}")
        assert history_response.status_code == 200
        
        data = history_response.json()
        assert data["conversation_id"] == conversation_id
        assert len(data["messages"]) > 0
    
    def test_conversation_format(self, client_with_mocks):
        """Test chat response format"""
        chat_request = {"message": "Hello"}
        response = client_with_mocks.post("/chat", json=chat_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "conversation_id" in data
        assert "message" in data
        assert isinstance(data["message"], list)
        
        for msg in data["message"]:
            assert "role" in msg
            assert "message" in msg
            assert msg["role"] in ["user", "bot"]
            assert len(msg["message"]) > 0

class TestErrorHandling:
    """Tests for error handling"""
    
    def test_invalid_json_request(self, client_with_mocks):
        """Test request with invalid JSON"""
        response = client_with_mocks.post("/chat", data="invalid json")
        assert response.status_code == 422
    
    def test_missing_message_field(self, client_with_mocks):
        """Test request without message field"""
        chat_request = {}
        response = client_with_mocks.post("/chat", json=chat_request)
        assert response.status_code == 422
    
    def test_empty_message_field(self, client_with_mocks):
        """Test request without message field"""
        chat_request = {"message": ""}
        response = client_with_mocks.post("/chat", json=chat_request)
        assert response.status_code == 422
    
    def test_whitespace_message_field(self, client_with_mocks):
        """Test request with whitespace-only message field"""
        chat_request = {"message": "   "}
        response = client_with_mocks.post("/chat", json=chat_request)
        assert response.status_code == 422
    
    def test_invalid_http_method(self, client_with_mocks):
        """Test invalid HTTP methods"""
        response = client_with_mocks.put("/chat")
        assert response.status_code == 405
        
        response = client_with_mocks.patch("/chat")
        assert response.status_code == 405

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
