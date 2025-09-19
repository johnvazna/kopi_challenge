import pytest
import time
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from src.main import app
from src.ai_service import OllamaAIService
from src.chat_logic import DebateChatbot
from src.memory_storage import InMemoryChatStorage

class TestAIIntegration:
    """Test cases for AI integration functionality"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_ai_service(self):
        """Mock AI service for testing"""
        mock_service = Mock(spec=OllamaAIService)
        mock_service.test_connection.return_value = True
        mock_service.generate_response.return_value = "I'm PRO pineapple on pizza! It's the perfect combination of sweet and savory!"
        return mock_service
    
    @pytest.fixture
    def mock_storage(self):
        """Mock storage for testing"""
        return InMemoryChatStorage()
    
    @pytest.fixture
    def chatbot_with_ai(self, mock_ai_service):
        """Create chatbot with mocked AI service"""
        return DebateChatbot(ai_service=mock_ai_service)

    def test_ai_service_connection(self, mock_ai_service):
        """Test AI service connection"""
        assert mock_ai_service.test_connection() == True
        
    def test_ai_service_generate_response(self, mock_ai_service):
        """Test AI service response generation"""
        response = mock_ai_service.generate_response(
            topic="Pineapple on pizza",
            stance="Pro",
            user_message="I think pineapple doesn't belong on pizza",
            conversation_history=None,
            is_initial=False
        )
        
        assert response is not None
        assert len(response) > 0
        mock_ai_service.generate_response.assert_called_once()
    
    def test_chatbot_initial_response_with_ai(self, chatbot_with_ai):
        """Test chatbot initial response using AI"""
        response = chatbot_with_ai.generate_initial_response()
        
        assert response is not None
        assert len(response) > 0
        assert "pineapple" in response.lower() or "pizza" in response.lower()
    
    def test_chatbot_debate_response_with_ai(self, chatbot_with_ai):
        """Test chatbot debate response using AI"""
        user_message = "I think pineapple on pizza is terrible!"
        response = chatbot_with_ai.generate_reply(user_message)
        
        assert response is not None
        assert len(response) > 0
        assert "pineapple" in response.lower() or "pizza" in response.lower()
    
    def test_ai_service_fallback_response(self):
        """Test AI service fallback when connection fails"""
        ai_service = OllamaAIService()
        
        with patch.object(ai_service, 'test_connection', return_value=False):
            response = ai_service.generate_response(
                topic="Pineapple on pizza",
                stance="Pro",
                user_message="Test message",
                conversation_history=None,
                is_initial=False
            )
            
            assert response is not None
            assert "technical difficulties" in response.lower() or "issues" in response.lower()
    
    def test_ai_service_timeout_handling(self):
        """Test AI service timeout handling"""
        ai_service = OllamaAIService()
        
        with patch('requests.post') as mock_post:
            mock_post.side_effect = Exception("Read timed out")
            
            response = ai_service.generate_response(
                topic="Pineapple on pizza",
                stance="Pro",
                user_message="Test message",
                conversation_history=None,
                is_initial=False
            )
            
            assert response is not None
            assert "technical difficulties" in response.lower() or "issues" in response.lower()
    
    def test_prompt_engineering_initial(self, mock_ai_service):
        """Test prompt engineering for initial responses"""
        mock_ai_service.generate_response.return_value = "Test response"
        
        response = mock_ai_service.generate_response(
            topic="Coffee vs Tea",
            stance="Pro Coffee",
            user_message="",
            conversation_history=None,
            is_initial=True
        )
        
        mock_ai_service.generate_response.assert_called_once_with(
            topic="Coffee vs Tea",
            stance="Pro Coffee",
            user_message="",
            conversation_history=None,
            is_initial=True
        )
    
    def test_prompt_engineering_debate(self, mock_ai_service):
        """Test prompt engineering for debate responses"""
        mock_ai_service.generate_response.return_value = "Test response"
        
        conversation_history = [
            {"message": "Hello", "is_user": True, "timestamp": "2023-01-01T00:00:00"},
            {"message": "Hi there!", "is_user": False, "timestamp": "2023-01-01T00:00:01"}
        ]
        
        response = mock_ai_service.generate_response(
            topic="Dark Mode vs Light Mode",
            stance="Pro Dark Mode",
            user_message="I prefer light mode",
            conversation_history=conversation_history,
            is_initial=False
        )
        
        mock_ai_service.generate_response.assert_called_once_with(
            topic="Dark Mode vs Light Mode",
            stance="Pro Dark Mode",
            user_message="I prefer light mode",
            conversation_history=conversation_history,
            is_initial=False
        )
    
    def test_chatbot_personality_summary_with_ai(self, chatbot_with_ai):
        """Test chatbot personality summary with AI"""
        summary = chatbot_with_ai.get_personality_summary()
        
        assert "AI-powered" in summary
        assert "debate-specialized" in summary
        assert "unshakeable" in summary.lower()
    
    def test_chatbot_personality_summary_fallback(self):
        """Test chatbot personality summary in fallback mode"""
        chatbot = DebateChatbot()
        summary = chatbot.get_personality_summary()
        
        assert "fallback mode" in summary or "AI-powered" in summary
        assert "debate-specialized" in summary
        assert "unshakeable" in summary.lower()


class TestAPIEndpoints:
    """Test cases for API endpoints with AI integration"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
    
    def test_personality_endpoint(self, client):
        """Test personality endpoint"""
        response = client.get("/personality")
        assert response.status_code == 200
        
        data = response.json()
        assert "personality" in data
        assert "description" in data
        assert "current_topic" in data
        assert "position" in data
        assert "AI-powered" in data["description"] or "fallback mode" in data["description"]
    
    def test_chat_endpoint_new_conversation(self, client):
        """Test chat endpoint for new conversation"""
        response = client.post(
            "/chat",
            json={"message": "Hello! Let's start a debate!"}
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert "conversation_id" in data
        assert "message" in data
        assert len(data["message"]) == 2
        
        user_msg = data["message"][0]
        bot_msg = data["message"][1]
        
        assert user_msg["role"] == "user"
        assert bot_msg["role"] == "bot"
        assert "message" in user_msg
        assert "message" in bot_msg
    
    def test_chat_endpoint_continue_conversation(self, client):
        """Test chat endpoint for continuing conversation"""
        response1 = client.post(
            "/chat",
            json={"message": "Hello! Let's debate!"}
        )
        
        assert response1.status_code == 200
        conversation_id = response1.json()["conversation_id"]
        
        response2 = client.post(
            "/chat",
            json={
                "conversation_id": conversation_id,
                "message": "I disagree with your stance!"
            }
        )
        
        assert response2.status_code == 200
        
        data = response2.json()
        assert data["conversation_id"] == conversation_id
        assert len(data["message"]) == 4
        
        messages = data["message"]
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "bot"
        assert messages[2]["role"] == "user"
        assert messages[3]["role"] == "bot"
    
    def test_chat_endpoint_invalid_conversation_id(self, client):
        """Test chat endpoint with invalid conversation ID"""
        response = client.post(
            "/chat",
            json={
                "conversation_id": "invalid-id",
                "message": "Hello!"
            }
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert "conversation_id" in data
        assert data["conversation_id"] != "invalid-id"
    
    def test_chat_endpoint_empty_message(self, client):
        """Test chat endpoint with empty message"""
        response = client.post(
            "/chat",
            json={"message": ""}
        )
        
        assert response.status_code == 400
    
    def test_chat_endpoint_whitespace_message(self, client):
        """Test chat endpoint with whitespace-only message"""
        response = client.post(
            "/chat",
            json={"message": "   "}
        )
        
        assert response.status_code == 400
    
    def test_chat_endpoint_long_message(self, client):
        """Test chat endpoint with message exceeding limit"""
        long_message = "a" * 1001
        
        response = client.post(
            "/chat",
            json={"message": long_message}
        )
        
        assert response.status_code == 400
    
    def test_get_conversation_history(self, client):
        """Test getting conversation history"""
        response1 = client.post(
            "/chat",
            json={"message": "Hello! Let's debate!"}
        )
        
        assert response1.status_code == 200
        conversation_id = response1.json()["conversation_id"]
        
        response2 = client.get(f"/chat/{conversation_id}")
        
        assert response2.status_code == 200
        
        data = response2.json()
        assert data["conversation_id"] == conversation_id
        assert "messages" in data
        assert "total_messages" in data
        assert "topic" in data
        assert "stance" in data
        assert data["total_messages"] == 2
    
    def test_get_nonexistent_conversation_history(self, client):
        """Test getting history for nonexistent conversation"""
        response = client.get("/chat/nonexistent-id")
        
        assert response.status_code == 404
    
    def test_delete_conversation(self, client):
        """Test deleting a conversation"""
        response1 = client.post(
            "/chat",
            json={"message": "Hello! Let's debate!"}
        )
        
        assert response1.status_code == 200
        conversation_id = response1.json()["conversation_id"]
        
        response2 = client.delete(f"/chat/{conversation_id}")
        
        assert response2.status_code == 200
        
        data = response2.json()
        assert data["conversation_id"] == conversation_id
        assert "deleted successfully" in data["message"]
        
        response3 = client.get(f"/chat/{conversation_id}")
        assert response3.status_code == 404
    
    def test_delete_nonexistent_conversation(self, client):
        """Test deleting a nonexistent conversation"""
        response = client.delete("/chat/nonexistent-id")
        
        assert response.status_code == 404
    
    def test_stats_endpoint(self, client):
        """Test stats endpoint"""
        response = client.get("/stats")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "storage" in data
        assert "chatbot_personality" in data
        assert "api_version" in data
        assert "config" in data
        assert data["api_version"] == "1.0.0"
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "description" in data
        assert "version" in data
        assert "endpoints" in data
        assert data["version"] == "1.0.0"

class TestPerformanceAndReliability:
    """Test cases for performance and reliability"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_concurrent_requests(self, client):
        """Test handling multiple concurrent requests"""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request():
            try:
                response = client.post(
                    "/chat",
                    json={"message": f"Hello from thread {threading.current_thread().ident}!"}
                )
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5
        assert all(status == 200 for status in results)
    
    def test_response_time_acceptable(self, client):
        """Test that response times are within acceptable limits"""
        start_time = time.time()
        
        response = client.post(
            "/chat",
            json={"message": "Hello! Let's debate!"}
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 30, f"Response time {response_time:.2f}s exceeds 30s limit"
    
    def test_memory_storage_persistence(self, client):
        """Test that in-memory storage persists during session"""
        response1 = client.post(
            "/chat",
            json={"message": "Hello! Let's debate!"}
        )
        
        assert response1.status_code == 200
        conversation_id = response1.json()["conversation_id"]
        
        response2 = client.post(
            "/chat",
            json={
                "conversation_id": conversation_id,
                "message": "I disagree!"
            }
        )
        
        assert response2.status_code == 200
        
        response3 = client.get(f"/chat/{conversation_id}")
        assert response3.status_code == 200
        
        data = response3.json()
        assert data["total_messages"] == 4

if __name__ == "__main__":
    pytest.main([__file__, "-v"])