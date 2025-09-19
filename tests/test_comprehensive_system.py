#!/usr/bin/env python3
"""
Comprehensive System Tests for Kopi Challenge AI-Powered Debate Chatbot
Tests all major functionality including AI integration, topic switching, and web interface
"""

import sys
import time
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_config
from src.ai_service import OllamaAIService
from src.chat_logic import DebateChatbot
from src.memory_storage import InMemoryChatStorage

class TestComprehensiveSystem:
    """Comprehensive system tests for the debate chatbot"""
    
    def __init__(self):
        self.config = get_config()
        self.base_url = self.config.get_test_base_url()
        self.ai_service = None
        self.chatbot = None
        self.storage = None
        
    def setup(self):
        """Setup test environment"""
        print("Setting up test environment...")
        
        self.ai_service = OllamaAIService()
        self.storage = InMemoryChatStorage()
        self.chatbot = DebateChatbot(ai_service=self.ai_service)
        
        print("Test environment setup complete")
        
    def test_ai_service_connection(self):
        """Test AI service connection and response generation"""
        print("\nTesting AI Service Connection...")
        
        try:
            is_available = self.ai_service.test_connection()
            assert is_available, "AI service connection failed"
            print("AI service connection successful")
            
            response = self.ai_service.generate_response(
                topic="Coffee is better than tea",
                stance="Pro Coffee",
                user_message="I think tea is better",
                is_initial=True
            )
            
            assert response is not None, "AI response generation failed"
            assert len(response) > 10, "AI response too short"
            assert "coffee" in response.lower() or "tea" in response.lower(), "Response not relevant to topic"
            
            print(f"AI response generated: {response[:50]}...")
            return True
            
        except Exception as e:
            print(f"AI service test failed: {e}")
            return False
    
    def test_chatbot_topic_selection(self):
        """Test chatbot topic selection and stance assignment"""
        print("\nTesting Chatbot Topic Selection...")
        
        try:
            topic, stance = self.chatbot.select_debate_topic()
            
            assert topic is not None, "Topic selection failed"
            assert stance is not None, "Stance assignment failed"
            assert len(topic) > 5, "Topic too short"
            assert len(stance) > 5, "Stance too short"
            
            print(f"Topic selected: {topic}")
            print(f"Stance assigned: {stance}")
            
            new_topic, new_stance = self.chatbot.detect_topic_change_request("Let's talk about coffee vs tea")
            
            assert new_topic is not None, "Topic change detection failed"
            assert new_stance is not None, "Stance change detection failed"
            assert "coffee" in new_topic.lower(), "Topic change not detected correctly"
            
            print(f"Topic change detected: {new_topic}")
            return True
            
        except Exception as e:
            print(f"Chatbot topic selection test failed: {e}")
            return False
    
    def test_storage_operations(self):
        """Test storage operations"""
        print("\nTesting Storage Operations...")
        
        try:
            conversation_id = self.storage.create_conversation("Test Topic", "Test Stance")
            
            assert conversation_id is not None, "Conversation creation failed"
            assert len(conversation_id) > 10, "Conversation ID too short"
            
            print(f"Conversation created: {conversation_id}")
            
            self.storage.save_message(conversation_id, "Test user message", is_user=True)
            self.storage.save_message(conversation_id, "Test bot message", is_user=False)
            
            messages = self.storage.get_conversation_history_limited(conversation_id)
            
            assert len(messages) == 2, f"Expected 2 messages, got {len(messages)}"
            assert messages[0]["message"] == "Test user message", "User message not saved correctly"
            assert messages[1]["message"] == "Test bot message", "Bot message not saved correctly"
            
            print("Messages saved and retrieved successfully")
            
            meta = self.storage.get_conversation_meta(conversation_id)
            
            assert meta is not None, "Conversation metadata not found"
            assert meta["topic"] == "Test Topic", "Topic metadata incorrect"
            assert meta["stance"] == "Test Stance", "Stance metadata incorrect"
            
            print("Conversation metadata correct")
            
            stats = self.storage.get_stats()
            
            assert "total_conversations" in stats, "Stats missing total_conversations"
            assert stats["total_conversations"] >= 1, "Stats incorrect"
            
            print("Storage stats correct")
            return True
            
        except Exception as e:
            print(f"Storage operations test failed: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("\nTesting API Endpoints...")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=self.config.TEST_TIMEOUT)
            assert response.status_code == 200, f"Health endpoint failed: {response.status_code}"
            
            health_data = response.json()
            assert health_data["status"] == "healthy", "Health status incorrect"
            
            print("Health endpoint working")
            
            response = requests.get(f"{self.base_url}/personality", timeout=self.config.TEST_TIMEOUT)
            assert response.status_code == 200, f"Personality endpoint failed: {response.status_code}"
            
            personality_data = response.json()
            assert "personality" in personality_data, "Personality data missing"
            assert "current_topic" in personality_data, "Current topic missing"
            
            print("Personality endpoint working")
            
            chat_request = {
                "message": "Let's start a debate about coffee vs tea"
            }
            
            response = requests.post(
                f"{self.base_url}/chat",
                json=chat_request,
                headers={"Content-Type": "application/json"},
                timeout=self.config.TEST_TIMEOUT
            )
            
            assert response.status_code == 200, f"Chat endpoint failed: {response.status_code}"
            
            chat_data = response.json()
            assert "conversation_id" in chat_data, "Conversation ID missing"
            assert "message" in chat_data, "Message data missing"
            assert len(chat_data["message"]) >= 2, "Insufficient messages in response"
            
            print("Chat endpoint working")
            print(f"Conversation ID: {chat_data['conversation_id']}")
            
            return True
            
        except Exception as e:
            print(f"API endpoints test failed: {e}")
            return False
    
    def test_topic_switching(self):
        """Test topic switching functionality"""
        print("\nTesting Topic Switching...")
        
        try:
            chat_request = {
                "message": "Hello, let's start a debate"
            }
            
            response = requests.post(
                f"{self.base_url}/chat",
                json=chat_request,
                headers={"Content-Type": "application/json"},
                timeout=self.config.TEST_TIMEOUT
            )
            
            assert response.status_code == 200, "Initial chat request failed"
            chat_data = response.json()
            conversation_id = chat_data["conversation_id"]
            
            print(f"Initial conversation started: {conversation_id}")
            
            topic_change_request = {
                "message": "Let's talk about coffee vs tea instead",
                "conversation_id": conversation_id
            }
            
            response = requests.post(
                f"{self.base_url}/chat",
                json=topic_change_request,
                headers={"Content-Type": "application/json"},
                timeout=self.config.TEST_TIMEOUT
            )
            
            assert response.status_code == 200, "Topic change request failed"
            topic_change_data = response.json()
            
            assert len(topic_change_data["message"]) >= 4, "Topic change didn't generate enough messages"
            
            print("Topic switching successful")
            
            continue_request = {
                "message": "I think tea is much better than coffee",
                "conversation_id": conversation_id
            }
            
            response = requests.post(
                f"{self.base_url}/chat",
                json=continue_request,
                headers={"Content-Type": "application/json"},
                timeout=self.config.TEST_TIMEOUT
            )
            
            assert response.status_code == 200, "Continued conversation failed"
            continue_data = response.json()
            
            last_message = continue_data["message"][-1]["message"]
            assert len(last_message) > 10, "Bot response too short"
            
            print("Continued conversation on new topic successful")
            return True
            
        except Exception as e:
            print(f"Topic switching test failed: {e}")
            return False
    
    def test_web_interface(self):
        """Test web interface accessibility"""
        print("\nTesting Web Interface...")
        
        try:
            response = requests.get(f"{self.base_url}/chat", timeout=self.config.TEST_TIMEOUT)
            assert response.status_code == 200, f"Chat interface failed: {response.status_code}"
            
            html_content = response.text
            assert "vue" in html_content.lower(), "Vue.js not found in HTML"
            assert "chat-container" in html_content, "Chat container not found"
            assert "New Chat" in html_content, "New Chat button not found"
            
            print("Chat interface accessible")
            
            css_response = requests.get(f"{self.base_url}/static/css/chat.css", timeout=self.config.TEST_TIMEOUT)
            assert css_response.status_code == 200, "CSS file not accessible"
            
            js_response = requests.get(f"{self.base_url}/static/js/chat.js", timeout=self.config.TEST_TIMEOUT)
            assert js_response.status_code == 200, "JavaScript file not accessible"
            
            print("Static files accessible")
            return True
            
        except Exception as e:
            print(f"Web interface test failed: {e}")
            return False
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\nTesting Error Handling...")
        
        try:
            invalid_request = {
                "message": "Test message",
                "conversation_id": "invalid-id-12345"
            }
            
            response = requests.post(
                f"{self.base_url}/chat",
                json=invalid_request,
                headers={"Content-Type": "application/json"},
                timeout=self.config.TEST_TIMEOUT
            )
            
            assert response.status_code == 200, "Invalid conversation ID handling failed"
            
            print("Invalid conversation ID handled correctly")
            
            empty_request = {
                "message": ""
            }
            
            response = requests.post(
                f"{self.base_url}/chat",
                json=empty_request,
                headers={"Content-Type": "application/json"},
                timeout=self.config.TEST_TIMEOUT
            )
            
            assert response.status_code == 422, "Empty message not rejected"
            
            print("Empty message rejected correctly")
            
            long_message = "A" * 2000
            long_request = {
                "message": long_message
            }
            
            response = requests.post(
                f"{self.base_url}/chat",
                json=long_request,
                headers={"Content-Type": "application/json"},
                timeout=self.config.TEST_TIMEOUT
            )
            
            assert response.status_code == 422, "Long message not rejected"
            
            print("Long message rejected correctly")
            return True
            
        except Exception as e:
            print(f"Error handling test failed: {e}")
            return False
    
    def test_performance(self):
        """Test system performance"""
        print("\nTesting Performance...")
        
        try:
            start_time = time.time()
            
            chat_request = {
                "message": "Quick test message"
            }
            
            response = requests.post(
                f"{self.base_url}/chat",
                json=chat_request,
                headers={"Content-Type": "application/json"},
                timeout=self.config.TEST_TIMEOUT
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200, "Performance test request failed"
            assert response_time < 30, f"Response time too slow: {response_time:.2f}s"
            
            print(f"Response time: {response_time:.2f}s")
            
            import threading
            import queue
            
            results = queue.Queue()
            
            def make_request():
                try:
                    req = {
                        "message": f"Concurrent test {threading.current_thread().ident}"
                    }
                    resp = requests.post(
                        f"{self.base_url}/chat",
                        json=req,
                        headers={"Content-Type": "application/json"},
                        timeout=self.config.TEST_TIMEOUT
                    )
                    results.put(resp.status_code == 200)
                except:
                    results.put(False)
            
            threads = []
            for i in range(3):
                thread = threading.Thread(target=make_request)
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            success_count = 0
            while not results.empty():
                if results.get():
                    success_count += 1
            
            assert success_count >= 2, f"Only {success_count}/3 concurrent requests succeeded"
            
            print(f"Concurrent requests: {success_count}/3 successful")
            return True
            
        except Exception as e:
            print(f"Performance test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("Starting Comprehensive System Tests")
        print("=" * 50)
        
        self.setup()
        
        tests = [
            ("AI Service Connection", self.test_ai_service_connection),
            ("Chatbot Topic Selection", self.test_chatbot_topic_selection),
            ("Storage Operations", self.test_storage_operations),
            ("API Endpoints", self.test_api_endpoints),
            ("Topic Switching", self.test_topic_switching),
            ("Web Interface", self.test_web_interface),
            ("Error Handling", self.test_error_handling),
            ("Performance", self.test_performance),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"{test_name} failed with exception: {e}")
                failed += 1
        
        print("\n" + "=" * 50)
        print(f"Test Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("All tests passed! System is working perfectly.")
            return True
        else:
            print("Some tests failed. Please check the issues above.")
            return False

def main():
    """Main test runner"""
    print("Kopi Challenge Comprehensive System Tests")
    print("Testing AI-powered debate chatbot functionality")
    print()
    
    tester = TestComprehensiveSystem()
    success = tester.run_all_tests()
    
    if success:
        print("\nAll systems operational!")
        sys.exit(0)
    else:
        print("\nSome tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()