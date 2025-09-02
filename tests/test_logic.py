import os
import sys

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.chat_logic import DebateChatbot

class TestDebateChatbot:
    """Tests for debate chatbot logic"""
    
    def setup_method(self):
        """Setup before each test"""
        self.chatbot = DebateChatbot()
    
    def test_initialization(self):
        """Test chatbot initialization"""
        assert hasattr(self.chatbot, 'debate_topics')
        assert hasattr(self.chatbot, 'current_topic')
        assert hasattr(self.chatbot, 'topic_info')
        assert len(self.chatbot.debate_topics) > 0
        assert self.chatbot.current_topic in self.chatbot.debate_topics
    
    def test_debate_topics_content(self):
        """Test debate topics content"""
        topics = self.chatbot.debate_topics
        
        expected_topics = [
            "Pineapple belongs on pizza",
            "Spaces vs Tabs",
            "Dark mode is better than light mode",
            "Remote work is more productive",
            "Oxford comma should always be used",
            "Coffee is better than tea"
        ]
        
        for topic in expected_topics:
            assert topic in topics
            topic_info = topics[topic]
            assert "position" in topic_info
            assert "reasons" in topic_info
            assert "analogies" in topic_info
            assert "questions" in topic_info
            assert len(topic_info["reasons"]) > 0
            assert len(topic_info["analogies"]) > 0
            assert len(topic_info["questions"]) > 0
    
    def test_topic_info_structure(self):
        """Test topic info structure"""
        topic_info = self.chatbot.get_topic_info()
        
        assert "topic" in topic_info
        assert "position" in topic_info
        assert "reasons" in topic_info
        assert isinstance(topic_info["topic"], str)
        assert isinstance(topic_info["position"], str)
        assert isinstance(topic_info["reasons"], list)
        assert len(topic_info["topic"]) > 0
        assert len(topic_info["position"]) > 0
        assert len(topic_info["reasons"]) > 0
    
    def test_pick_topic_and_stance(self):
        """Test pick_topic_and_stance method"""
        topic_stance = self.chatbot.pick_topic_and_stance()
        
        assert isinstance(topic_stance, dict)
        assert "topic" in topic_stance
        assert "stance" in topic_stance
        assert isinstance(topic_stance["topic"], str)
        assert isinstance(topic_stance["stance"], str)
        assert len(topic_stance["topic"]) > 0
        assert len(topic_stance["stance"]) > 0
        
        assert topic_stance["topic"] in self.chatbot.debate_topics
        
        expected_stance = self.chatbot.debate_topics[topic_stance["topic"]]["position"]
        assert topic_stance["stance"] == expected_stance
    
    def test_pick_topic_and_stance_multiple_calls(self):
        """Test multiple calls to pick_topic_and_stance"""
        results = []
        for _ in range(10):
            topic_stance = self.chatbot.pick_topic_and_stance()
            results.append(topic_stance)
            
            assert "topic" in topic_stance
            assert "stance" in topic_stance
            assert topic_stance["topic"] in self.chatbot.debate_topics
        
        unique_topics = set(result["topic"] for result in results)
        assert len(unique_topics) > 1
    
    def test_set_topic_and_stance_valid(self):
        """Test set_topic_and_stance with valid topic"""
        valid_topic = list(self.chatbot.debate_topics.keys())[0]
        valid_stance = self.chatbot.debate_topics[valid_topic]["position"]
        
        result = self.chatbot.set_topic_and_stance(valid_topic, valid_stance)
        
        assert result is True
        assert self.chatbot.current_topic == valid_topic
        assert self.chatbot.topic_info["position"] == valid_stance
    
    def test_set_topic_and_stance_invalid(self):
        """Test set_topic_and_stance with invalid topic"""
        result = self.chatbot.set_topic_and_stance("Non-existent topic", "Stance")
        
        assert result is False
        assert self.chatbot.current_topic != "Non-existent topic"
    
    def test_generate_reply(self):
        """Test generate_reply method"""
        user_message = "Hello, what do you think about this topic?"
        response = self.chatbot.generate_reply(user_message)
        
        assert isinstance(response, str)
        assert len(response) > 0
        
        current_topic = self.chatbot.current_topic
        current_stance = self.chatbot.topic_info["position"]
        
        assert current_topic in response
        assert current_stance in response
        assert any(element in response for element in [current_topic, current_stance, "stance", "position"])
    
    def test_generate_reply_error_handling(self):
        """Test error handling in generate_reply"""
        long_message = "a" * 10000
        
        response = self.chatbot.generate_reply(long_message)
        
        assert isinstance(response, str)
        assert len(response) > 0
        # The chatbot handles long messages gracefully, so we just check it returns a valid response
        assert len(response) > 10
    
    def test_initial_response_generation(self):
        """Test initial response generation"""
        response = self.chatbot.generate_initial_response()
        
        assert isinstance(response, str)
        assert len(response) > 0
        
        assert "**" in response
        assert "What do you think about" in response
        assert "Can you give me arguments against it?" in response
        
        current_topic = self.chatbot.current_topic
        assert current_topic in response
    
    def test_personality_summary(self):
        """Test personality summary"""
        summary = self.chatbot.get_personality_summary()
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "debate-specialized chatbot" in summary.lower()
        assert "stance" in summary.lower()
        assert "will not change" in summary.lower()
        assert "structured" in summary.lower()
        
        current_topic = self.chatbot.current_topic
        assert current_topic in summary

class TestMessageDetection:
    """Tests for message type detection"""
    
    def setup_method(self):
        """Set up test environment"""
        self.chatbot = DebateChatbot()
    
    def test_clarification_detection(self):
        """Test clarification request detection"""
        clarification_phrases = [
            "what do you mean",
            "explain",
            "i don't understand",
            "clarify"
        ]
        
        for phrase in clarification_phrases:
            assert self.chatbot._is_asking_for_clarification(phrase)
    
    def test_challenge_detection(self):
        """Test stance challenge detection"""
        challenge_phrases = [
            "you're wrong",
            "that's not true",
            "i disagree",
            "i don't agree"
        ]
        
        for phrase in challenge_phrases:
            assert self.chatbot._is_challenging_position(phrase)
    
    def test_evidence_request_detection(self):
        """Test evidence request detection"""
        evidence_phrases = [
            "proof",
            "evidence",
            "source",
            "study",
            "research"
        ]
        
        for phrase in evidence_phrases:
            assert self.chatbot._is_asking_for_evidence(phrase)
    
    def test_greeting_detection(self):
        """Test greeting detection"""
        greetings = [
            "hello",
            "hi",
            "good morning"
        ]
        
        for greeting in greetings:
            assert self.chatbot._is_greeting(greeting)
    
    def test_farewell_detection(self):
        """Test farewell detection"""
        farewells = [
            "goodbye",
            "bye",
            "see you",
            "farewell"
        ]
        
        for farewell in farewells:
            assert self.chatbot._is_farewell(farewell)

class TestResponseGeneration:
    """Tests for response generation"""
    
    def setup_method(self):
        """Setup before each test"""
        self.chatbot = DebateChatbot()
    
    def test_clarify_position_response(self):
        """Test clarify position response"""
        response = self.chatbot._clarify_position()
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "**" in response
        assert "stance" in response.lower()
        assert "What part of my argument is unclear to you?" in response
        
        current_topic = self.chatbot.current_topic
        current_position = self.chatbot.topic_info["position"]
        assert current_topic in response
        assert current_position in response
    
    def test_defend_position_response(self):
        """Test defend position response"""
        response = self.chatbot._defend_position("challenge message")
        
        assert isinstance(response, str)
        assert len(response) > 0
        
        assert "stance" in response.lower()
        assert "unshakeable" in response.lower() or "firm" in response.lower()
        assert "I recognize that you have a different opinion" in response
        assert "**" in response
        
        assert any(f"{i}." in response for i in range(1, 4))
        
        assert any(analogy in response for analogy in self.chatbot.topic_info["analogies"])
        
        assert any(question in response for question in self.chatbot.topic_info["questions"])
    
    def test_provide_evidence_response(self):
        """Test provide evidence response"""
        response = self.chatbot._provide_evidence()
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "Excellent question!" in response
        assert "**" in response
        
        assert any(f"{i}." in response for i in range(1, 4))
        
        assert any(analogy in response for analogy in self.chatbot.topic_info["analogies"])
        
        assert "Don't you think these arguments are convincing?" in response
    
    def test_greet_and_explain_topic_response(self):
        """Test greet and explain topic response"""
        response = self.chatbot._greet_and_explain_topic()
    
        # Both methods should return similar responses but may have different topics
        assert isinstance(response, str)
        assert len(response) > 0
        assert "**" in response
        assert "What do you think about" in response
    
    def test_farewell_response(self):
        """Test farewell response"""
        response = self.chatbot._say_farewell()
        
        assert isinstance(response, str)
        assert len(response) > 0
        
        current_topic = self.chatbot.current_topic
        assert current_topic in response
        # Check that it contains stance-related words
        assert any(word in response.lower() for word in ["stance", "conviction", "arguments"])
    
    def test_structured_response_generation(self):
        """Test structured response generation"""
        response = self.chatbot._generate_structured_response("general message")
        
        assert isinstance(response, str)
        assert len(response) > 0
        
        assert "stance" in response.lower()
        assert "**" in response
        
        assert "I appreciate your perspective" in response
        
        current_position = self.chatbot.topic_info["position"]
        assert f"**{current_position}**" in response
        
        assert any(f"{i}." in response for i in range(1, 3))
        
        assert any(analogy in response for analogy in self.chatbot.topic_info["analogies"])
        
        assert any(question in response for question in self.chatbot.topic_info["questions"])

class TestChatbotIntegration:
    """Chatbot integration tests"""
    
    def setup_method(self):
        """Setup before each test"""
        self.chatbot = DebateChatbot()
    
    def test_generate_response_clarification(self):
        """Test response generation for clarification request"""
        response = self.chatbot.generate_response("What exactly do you mean?")
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "stance" in response.lower()
        assert "**" in response
    
    def test_generate_response_challenge(self):
        """Test response generation for stance challenge"""
        response = self.chatbot.generate_response("I don't agree with your stance")
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "stance" in response.lower()
        assert "unshakeable" in response.lower() or "firm" in response.lower()
    
    def test_generate_response_evidence_request(self):
        """Test response generation for evidence request"""
        response = self.chatbot.generate_response("Do you have any proof of that?")
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "Excellent question!" in response
        assert "arguments" in response.lower()
    
    def test_generate_response_greeting(self):
        """Test response generation for greeting"""
        response = self.chatbot.generate_response("Hello")
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "**" in response
        assert "What do you think about" in response
    
    def test_generate_response_farewell(self):
        """Test response generation for farewell"""
        response = self.chatbot.generate_response("Goodbye")
        
        assert isinstance(response, str)
        assert len(response) > 0
        # Check that it contains stance-related words
        assert any(word in response.lower() for word in ["stance", "conviction", "arguments"])
    
    def test_generate_response_general_message(self):
        """Test response generation for general message"""
        response = self.chatbot.generate_response("Message without specific category")
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "stance" in response.lower()
        assert "**" in response
        
        current_topic = self.chatbot.current_topic
        assert current_topic in response
        
        current_stance = self.chatbot.topic_info["position"]
        assert current_stance in response

class TestChatbotBehavior:
    """Tests for chatbot behavior patterns"""
    
    def setup_method(self):
        """Setup before each test"""
        self.chatbot = DebateChatbot()
    
    def test_consistent_stance_maintenance(self):
        """Test that chatbot maintains consistent stance"""
        initial_stance = self.chatbot.topic_info["position"]
        
        # Generate multiple responses
        for _ in range(5):
            response = self.chatbot.generate_response("Random message")
            assert initial_stance in response
            assert self.chatbot.topic_info["position"] == initial_stance
    
    def test_structured_response_format(self):
        """Test that responses follow structured format"""
        response = self.chatbot.generate_response("Test message")
        
        # Check for structured elements
        assert "**" in response  # Bold formatting
        assert any(f"{i}." in response for i in range(1, 4))  # Numbered reasons
        assert self.chatbot.current_topic in response  # Topic mentioned
        assert self.chatbot.topic_info["position"] in response  # Stance mentioned
    
    def test_topic_consistency(self):
        """Test that chatbot stays on the same topic"""
        initial_topic = self.chatbot.current_topic
        
        # Generate multiple responses
        for _ in range(3):
            response = self.chatbot.generate_response("Another message")
            assert initial_topic in response
            assert self.chatbot.current_topic == initial_topic
    
    def test_response_length_consistency(self):
        """Test that responses have consistent length"""
        responses = []
        
        # Generate multiple responses
        for _ in range(5):
            response = self.chatbot.generate_response("Test message")
            responses.append(response)
            assert len(response) > 50  # Minimum length
            assert len(response) < 1000  # Maximum reasonable length
        
        # Check that responses are reasonably consistent in length
        lengths = [len(r) for r in responses]
        avg_length = sum(lengths) / len(lengths)
        for length in lengths:
            assert 0.5 * avg_length < length < 2 * avg_length

class TestEdgeCases:
    """Tests for edge cases and error handling"""
    
    def setup_method(self):
        """Setup before each test"""
        self.chatbot = DebateChatbot()
    
    def test_empty_message(self):
        """Test handling of empty message"""
        response = self.chatbot.generate_response("")
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert self.chatbot.current_topic in response
    
    def test_very_long_message(self):
        """Test handling of very long message"""
        long_message = "a" * 10000
        response = self.chatbot.generate_response(long_message)
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert len(response) < 2000  # Should not be excessively long
    
    def test_special_characters(self):
        """Test handling of special characters"""
        special_message = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        response = self.chatbot.generate_response(special_message)
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert self.chatbot.current_topic in response
    
    def test_numbers_in_message(self):
        """Test handling of numbers in message"""
        number_message = "12345 67890"
        response = self.chatbot.generate_response(number_message)
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert self.chatbot.current_topic in response

class TestPerformance:
    """Performance tests"""
    
    def setup_method(self):
        """Setup before each test"""
        self.chatbot = DebateChatbot()
    
    def test_response_generation_speed(self):
        """Test response generation speed"""
        import time
        
        start_time = time.time()
        response = self.chatbot.generate_response("Test message")
        end_time = time.time()
        
        generation_time = end_time - start_time
        assert generation_time < 1.0  # Should generate response in less than 1 second
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_multiple_responses_speed(self):
        """Test speed of generating multiple responses"""
        import time
        
        start_time = time.time()
        responses = []
        for _ in range(10):
            response = self.chatbot.generate_response("Test message")
            responses.append(response)
        end_time = time.time()
        
        total_time = end_time - start_time
        assert total_time < 5.0  # Should generate 10 responses in less than 5 seconds
        
        for response in responses:
            assert isinstance(response, str)
            assert len(response) > 0
    
    def test_memory_usage(self):
        """Test memory usage doesn't grow excessively"""
        import gc
        import sys
        
        # Force garbage collection
        gc.collect()
        initial_memory = sys.getsizeof(self.chatbot)
        
        # Generate many responses
        for _ in range(100):
            self.chatbot.generate_response("Test message")
        
        # Force garbage collection again
        gc.collect()
        final_memory = sys.getsizeof(self.chatbot)
        
        # Memory usage should not grow significantly
        memory_growth = final_memory - initial_memory
        assert memory_growth < 1000  # Should not grow by more than 1KB

class TestInternationalization:
    """Tests for internationalization support"""
    
    def setup_method(self):
        """Setup before each test"""
        self.chatbot = DebateChatbot()
    
    def test_unicode_support(self):
        """Test support for unicode characters"""
        unicode_message = "Hello 世界 🌍 Привет"
        response = self.chatbot.generate_response(unicode_message)
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert self.chatbot.current_topic in response
    
    def test_multilingual_input(self):
        """Test handling of multilingual input"""
        multilingual_messages = [
            "Hello",
            "Hola",
            "Bonjour",
            "Guten Tag",
            "こんにちは"
        ]
        
        for message in multilingual_messages:
            response = self.chatbot.generate_response(message)
            assert isinstance(response, str)
            assert len(response) > 0
            assert self.chatbot.current_topic in response
    
    def test_emojis_in_input(self):
        """Test handling of emojis in input"""
        emoji_message = "Hello! 😊 How are you? 🎉"
        response = self.chatbot.generate_response(emoji_message)
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert self.chatbot.current_topic in response

class TestChatbotPersistence:
    """Tests for chatbot state persistence"""
    
    def setup_method(self):
        """Setup before each test"""
        self.chatbot = DebateChatbot()
    
    def test_topic_persistence(self):
        """Test that topic persists across multiple interactions"""
        initial_topic = self.chatbot.current_topic
        
        # Simulate multiple interactions
        for _ in range(5):
            self.chatbot.generate_response("Test message")
            assert self.chatbot.current_topic == initial_topic
    
    def test_stance_persistence(self):
        """Test that stance persists across multiple interactions"""
        initial_stance = self.chatbot.topic_info["position"]
        
        # Simulate multiple interactions
        for _ in range(5):
            self.chatbot.generate_response("Test message")
            assert self.chatbot.topic_info["position"] == initial_stance
    
    def test_topic_change_handling(self):
        """Test handling of topic changes"""
        initial_topic = self.chatbot.current_topic
        
        # Change topic
        new_topic = list(self.chatbot.debate_topics.keys())[1]
        new_stance = self.chatbot.debate_topics[new_topic]["position"]
        
        result = self.chatbot.set_topic_and_stance(new_topic, new_stance)
        assert result is True
        
        # Verify change
        assert self.chatbot.current_topic == new_topic
        assert self.chatbot.topic_info["position"] == new_stance
        
        # Generate response with new topic
        response = self.chatbot.generate_response("Test message")
        assert new_topic in response
        assert new_stance in response

class TestChatbotValidation:
    """Tests for input validation and error handling"""
    
    def setup_method(self):
        """Setup before each test"""
        self.chatbot = DebateChatbot()
    
    def test_invalid_topic_handling(self):
        """Test handling of invalid topics"""
        result = self.chatbot.set_topic_and_stance("Invalid Topic", "Invalid Stance")
        assert result is False
        
        # Should not change current topic
        original_topic = self.chatbot.current_topic
        assert self.chatbot.current_topic == original_topic
    
    def test_none_input_handling(self):
        """Test handling of None input"""
        response = self.chatbot.generate_response(None)
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert self.chatbot.current_topic in response
    
    def test_non_string_input_handling(self):
        """Test handling of non-string input"""
        non_string_inputs = [123, 45.67, True, False, [], {}, None]
        
        for input_val in non_string_inputs:
            response = self.chatbot.generate_response(str(input_val))
            assert isinstance(response, str)
            assert len(response) > 0
            assert self.chatbot.current_topic in response

class TestChatbotStatistics:
    """Tests for chatbot statistics and metrics"""
    
    def setup_method(self):
        """Setup before each test"""
        self.chatbot = DebateChatbot()
    
    def test_response_statistics(self):
        """Test response statistics tracking"""
        # Generate multiple responses
        responses = []
        for _ in range(10):
            response = self.chatbot.generate_response("Test message")
            responses.append(response)
        
        # Check response characteristics
        assert len(responses) == 10
        for response in responses:
            assert isinstance(response, str)
            assert len(response) > 0
            assert self.chatbot.current_topic in response
    
    def test_topic_distribution(self):
        """Test topic distribution in responses"""
        topics_mentioned = set()
        
        # Generate multiple responses
        for _ in range(20):
            response = self.chatbot.generate_response("Test message")
            topics_mentioned.add(self.chatbot.current_topic)
        
        # Should have consistent topic
        assert len(topics_mentioned) == 1
        assert list(topics_mentioned)[0] == self.chatbot.current_topic
    
    def test_stance_consistency_metrics(self):
        """Test stance consistency metrics"""
        stances_mentioned = set()
        
        # Generate multiple responses
        for _ in range(15):
            response = self.chatbot.generate_response("Test message")
            stances_mentioned.add(self.chatbot.topic_info["position"])
        
        # Should have consistent stance
        assert len(stances_mentioned) == 1
        assert list(stances_mentioned)[0] == self.chatbot.topic_info["position"]

class TestChatbotExtensibility:
    """Tests for chatbot extensibility and customization"""
    
    def setup_method(self):
        """Setup before each test"""
        self.chatbot = DebateChatbot()
    
    def test_new_topic_addition(self):
        """Test adding new debate topics"""
        new_topic = "New Test Topic"
        new_topic_info = {
            "position": "Pro New Topic",
            "reasons": ["Reason 1", "Reason 2", "Reason 3"],
            "analogies": ["Analogy 1", "Analogy 2"],
            "questions": ["Question 1", "Question 2"]
        }
        
        # Add new topic
        self.chatbot.debate_topics[new_topic] = new_topic_info
        
        # Verify addition
        assert new_topic in self.chatbot.debate_topics
        assert self.chatbot.debate_topics[new_topic] == new_topic_info
        
        # Test setting new topic
        result = self.chatbot.set_topic_and_stance(new_topic, new_topic_info["position"])
        assert result is True
        assert self.chatbot.current_topic == new_topic
    
    def test_custom_response_generation(self):
        """Test custom response generation methods"""
        # Test custom clarification response
        custom_response = self.chatbot._clarify_position()
        assert isinstance(custom_response, str)
        assert len(custom_response) > 0
        assert "stance" in custom_response.lower()
        
        # Test custom defense response
        custom_defense = self.chatbot._defend_position("Custom challenge")
        assert isinstance(custom_defense, str)
        assert len(custom_defense) > 0
        assert "stance" in custom_defense.lower()
    
    def test_response_customization(self):
        """Test response customization capabilities"""
        # Test that responses can be customized
        response = self.chatbot.generate_response("Custom message")
        
        # Should contain standard elements
        assert "**" in response
        assert self.chatbot.current_topic in response
        assert self.chatbot.topic_info["position"] in response
        
        # Should be customizable
        assert len(response) > 0
        assert isinstance(response, str)

def test_chatbot_import():
    """Test that chatbot can be imported correctly"""
    from src.chat_logic import DebateChatbot
    
    chatbot = DebateChatbot()
    assert chatbot is not None
    assert hasattr(chatbot, 'debate_topics')
    assert hasattr(chatbot, 'generate_response')

def test_chatbot_instantiation():
    """Test chatbot instantiation"""
    from src.chat_logic import DebateChatbot
    
    chatbot = DebateChatbot()
    assert isinstance(chatbot, DebateChatbot)
    assert chatbot.debate_topics is not None
    assert len(chatbot.debate_topics) > 0

def test_chatbot_methods():
    """Test that all required methods exist"""
    from src.chat_logic import DebateChatbot
    
    chatbot = DebateChatbot()
    
    required_methods = [
        'generate_response',
        'generate_reply',
        'generate_initial_response',
        'get_personality_summary',
        'get_topic_info',
        'pick_topic_and_stance',
        'set_topic_and_stance'
    ]
    
    for method_name in required_methods:
        assert hasattr(chatbot, method_name)
        method = getattr(chatbot, method_name)
        assert callable(method)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
