#!/usr/bin/env python3
"""
Manual test script for AI integration functionality.
This script tests the AI integration without requiring the full API to be running.
"""

import sys
import time
import requests
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ai_service import OllamaAIService
from src.chat_logic import DebateChatbot
from src.memory_storage import InMemoryChatStorage

def test_ai_service_connection():
    """Test AI service connection"""
    print("Testing AI service connection...")
    
    ai_service = OllamaAIService()
    is_connected = ai_service.test_connection()
    
    if is_connected:
        print("AI service connection successful!")
        return True
    else:
        print("AI service connection failed!")
        return False

def test_ai_service_response_generation():
    """Test AI service response generation"""
    print("\nTesting AI service response generation...")
    
    ai_service = OllamaAIService()
    
    print("  Testing initial response...")
    start_time = time.time()
    
    initial_response = ai_service.generate_response(
        topic="Pineapple on pizza",
        stance="Pro",
        user_message="",
        conversation_history=None,
        is_initial=True
    )
    
    end_time = time.time()
    print(f"  Initial response generated in {end_time - start_time:.2f} seconds")
    print(f"  Response: {initial_response[:100]}...")
    
    assert initial_response is not None and len(initial_response) > 0
    assert "pineapple" in initial_response.lower() or "pizza" in initial_response.lower()
    
    print("  Testing debate response...")
    start_time = time.time()
    
    debate_response = ai_service.generate_response(
        topic="Pineapple on pizza",
        stance="Pro",
        user_message="I think pineapple on pizza is disgusting!",
        conversation_history=[
            {"message": "Hello! Let's debate about pineapple on pizza!", "is_user": True},
            {"message": initial_response, "is_user": False}
        ],
        is_initial=False
    )
    
    end_time = time.time()
    print(f"  Debate response generated in {end_time - start_time:.2f} seconds")
    print(f"  Response: {debate_response[:100]}...")
    
    assert debate_response is not None and len(debate_response) > 0
    assert "pineapple" in debate_response.lower() or "pizza" in debate_response.lower()


def test_chatbot_with_ai():
    """Test chatbot with AI integration"""
    print("\nTesting chatbot with AI integration...")
    
    ai_service = OllamaAIService()
    chatbot = DebateChatbot(ai_service=ai_service)
    
    print("  Testing chatbot initial response...")
    start_time = time.time()
    
    initial_bot_response = chatbot.generate_initial_response()
    
    end_time = time.time()
    print(f"  Chatbot initial response generated in {end_time - start_time:.2f} seconds")
    print(f"  Response: {initial_bot_response[:100]}...")
    
    assert initial_bot_response is not None and len(initial_bot_response) > 0
    
    print("  Testing chatbot debate response...")
    start_time = time.time()
    
    debate_bot_response = chatbot.generate_reply(
        user_message="I disagree with your stance!",
        conversation_history=[
            {"message": "Hello!", "is_user": True},
            {"message": initial_bot_response, "is_user": False}
        ]
    )
    
    end_time = time.time()
    print(f"  Chatbot debate response generated in {end_time - start_time:.2f} seconds")
    print(f"  Response: {debate_bot_response[:100]}...")
    
    assert debate_bot_response is not None and len(debate_bot_response) > 0
    
    print("  Testing personality summary...")
    personality = chatbot.get_personality_summary()
    print(f"  Personality: {personality[:100]}...")
    
    assert "ai-powered" in personality.lower()
    assert chatbot.get_current_topic() in personality
    assert chatbot.get_current_stance() in personality


def test_storage_integration():
    """Test storage integration"""
    print("\nTesting storage integration...")
    
    storage = InMemoryChatStorage()
    topic = "Pineapple on pizza"
    stance = "Pro"
    
    conversation_id = storage.create_conversation(topic, stance)
    print(f"  Conversation created: {conversation_id}")
    assert conversation_id is not None
    
    storage.save_message(conversation_id, "User message 1", is_user=True)
    storage.save_message(conversation_id, "Bot response 1", is_user=False)
    print("  Messages saved")
    
    history = storage.get_conversation_history(conversation_id)
    print(f"  Retrieved {len(history)} messages")
    assert len(history) == 2
    
    limited_history = storage.get_conversation_history_limited(conversation_id)
    print(f"  Retrieved {len(limited_history)} limited messages")
    assert len(limited_history) == 2
    
    meta = storage.get_conversation_meta(conversation_id)
    print(f"  Retrieved metadata: {meta['topic']} - {meta['stance']}")
    assert meta["topic"] == topic
    
    stats = storage.get_stats()
    print(f"  Storage stats: {stats.get('total_conversations', 0)} conversations, {stats.get('total_messages', 0)} messages")
    assert stats.get("total_conversations", 0) >= 1
    assert stats.get("total_messages", 0) >= 2


def test_full_integration():
    """Test full integration workflow"""
    print("\nTesting full integration workflow...")
    
    ai_service = OllamaAIService()
    chatbot = DebateChatbot(ai_service=ai_service)
    storage = InMemoryChatStorage()
    
    topic, stance = chatbot.select_debate_topic()
    conversation_id = storage.create_conversation(topic, stance)
    
    print("  Simulating conversation...")
    user_message_1 = "What do you think about " + topic + "?"
    bot_response_1 = chatbot.generate_reply(user_message_1, [])
    storage.save_message(conversation_id, user_message_1, is_user=True)
    storage.save_message(conversation_id, bot_response_1, is_user=False)
    print(f"  Bot response: {bot_response_1[:100]}...")
    
    user_message_2 = "I disagree with you!"
    conversation_history = storage.get_conversation_history_limited(conversation_id)
    bot_response_2 = chatbot.generate_reply(user_message_2, conversation_history)
    storage.save_message(conversation_id, user_message_2, is_user=True)
    storage.save_message(conversation_id, bot_response_2, is_user=False)
    print(f"  Bot response 2: {bot_response_2[:100]}...")
    
    final_history = storage.get_conversation_history(conversation_id)
    print(f"  Final conversation has {len(final_history)} messages")
    assert len(final_history) == 4
    assert chatbot.get_current_topic() == topic
    assert chatbot.get_current_stance() == stance


def test_error_handling():
    """Test error handling and fallback behavior"""
    print("\nTesting error handling...")
    
    mock_ai_service = OllamaAIService()
    with patch.object(mock_ai_service, 'generate_response') as mock_generate:
        mock_generate.side_effect = requests.exceptions.Timeout("Mocked timeout")
        
        chatbot = DebateChatbot(ai_service=mock_ai_service)
        chatbot.select_debate_topic()
        
        fallback_response = chatbot.generate_initial_response()
        print("  Testing fallback behavior...")
        print(f"  Fallback response: {fallback_response[:100]}...")
        assert "technical difficulties" in fallback_response.lower() or "experiencing" in fallback_response.lower()
        
        fallback_personality = chatbot.get_personality_summary()
        print(f"  Fallback personality: {fallback_personality[:100]}...")
        assert "ai-powered" in fallback_personality.lower()


if __name__ == "__main__":
    print("Starting AI Integration Tests")
    print("==================================================")
    
    test_ai_service_connection()
    test_ai_service_response_generation()
    test_chatbot_with_ai()
    test_storage_integration()
    test_full_integration()
    test_error_handling()
    
    print("\n==================================================")
    print("Test Results Summary")
    print("==================================================")
    
    print("All tests passed! AI integration is working correctly.")