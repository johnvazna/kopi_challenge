import logging
import random
from typing import Dict, List

from .ai_service import OllamaAIService

logger = logging.getLogger(__name__)

class DebateChatbot:
    def __init__(self, ai_service: OllamaAIService = None):
        self.ai_service = ai_service or OllamaAIService()
        
        if not self.ai_service.test_connection():
            logger.warning("AI service connection failed, using fallback mode")
        
        self.debate_topics = [
            "Pineapple belongs on pizza",
            "Spaces vs Tabs",
            "Dark mode is better than light mode",
            "Coffee is better than tea",
            "Remote work is more productive",
            "Oxford comma should always be used",
            "Cats are better than dogs",
            "Video games are art",
            "Social media is harmful",
            "Electric cars are the future"
        ]
        
        self.current_topic = None
        self.current_stance = None
        
        logger.info("DebateChatbot initialized with AI service")
    
    def select_debate_topic(self) -> tuple[str, str]:
        topic = random.choice(self.debate_topics)
        
        if "Pineapple" in topic:
            stance = "Pro"
        elif "Spaces vs Tabs" in topic:
            stance = "Pro Tabs"
        elif "Dark mode" in topic:
            stance = "Pro Dark Mode"
        elif "Coffee" in topic:
            stance = "Pro Coffee"
        elif "Remote work" in topic:
            stance = "Pro Remote Work"
        elif "Oxford comma" in topic:
            stance = "Pro Oxford Comma"
        elif "Cats" in topic:
            stance = "Pro Cats"
        elif "Video games" in topic:
            stance = "Pro Video Games"
        elif "Social media" in topic:
            stance = "Anti Social Media"
        elif "Electric cars" in topic:
            stance = "Pro Electric Cars"
        else:
            stance = "Pro"
        
        self.current_topic = topic
        self.current_stance = stance
        
        logger.info(f"Debate topic selected: {topic} - Stance: {stance}")
        return topic, stance
    
    def generate_initial_response(self) -> str:
        if not self.current_topic or not self.current_stance:
            self.select_debate_topic()
        
        try:
            response = self.ai_service.generate_response(
                topic=self.current_topic,
                stance=self.current_stance,
                user_message="",
                conversation_history=None,
                is_initial=True
            )
            
            logger.info(f"Generated AI initial response for topic: {self.current_topic}, stance: {self.current_stance}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating initial response: {e}")
            return self._get_fallback_response()
    
    def generate_reply(self, user_message: str, conversation_history: List[Dict] = None) -> str:
        if not self.current_topic or not self.current_stance:
            self.select_debate_topic()
        
        try:
            response = self.ai_service.generate_response(
                topic=self.current_topic,
                stance=self.current_stance,
                user_message=user_message,
                conversation_history=conversation_history,
                is_initial=False
            )
            
            logger.info(f"Generated AI response for topic: {self.current_topic}, stance: {self.current_stance}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating reply: {e}")
            return self._get_fallback_response()
    
    def generate_response(self, user_message: str, conversation_history: List[Dict] = None) -> str:
        return self.generate_reply(user_message, conversation_history)
    
    def _get_fallback_response(self) -> str:
        if not self.current_topic or not self.current_stance:
            self.select_debate_topic()
        
        return f"I'm experiencing technical difficulties, but my stance on **{self.current_topic}** remains **{self.current_stance}**. Let's continue this debate!"
    
    def get_personality_summary(self) -> str:
        if not self.current_topic or not self.current_stance:
            self.select_debate_topic()
        
        return (
            f"I am an AI-powered debate-specialized chatbot that defends the **{self.current_stance}** stance on **{self.current_topic}**. "
            f"I use advanced AI to generate dynamic, engaging responses while maintaining my unshakeable position. "
            f"My responses include clear arguments, analogies, and questions to continue the debate. "
            f"My stance is permanent and I will never change my opinion, regardless of the arguments presented."
        )
    
    def get_current_topic(self) -> str:
        if not self.current_topic:
            self.select_debate_topic()
        return self.current_topic
    
    def get_current_stance(self) -> str:
        if not self.current_stance:
            self.select_debate_topic()
        return self.current_stance
    
    def set_conversation_topic(self, topic: str, stance: str):
        """Set the current conversation topic and stance"""
        self.current_topic = topic
        self.current_stance = stance
        logger.info(f"Conversation topic set to: {topic} - Stance: {stance}")
    
    def detect_topic_change_request(self, user_message: str) -> tuple:
        """Detect if user wants to change topic and return new topic/stance"""
        message_lower = user_message.lower()
        
        if "coffee" in message_lower and "tea" in message_lower:
            return "Coffee is better than tea", "Pro Coffee"
        elif "spaces" in message_lower and "tabs" in message_lower:
            return "Spaces vs Tabs", "Pro Tabs"
        elif "cats" in message_lower and "dogs" in message_lower:
            return "Cats vs Dogs", "Pro Cats"
        elif "dark mode" in message_lower and "light mode" in message_lower:
            return "Dark mode vs Light mode", "Pro Dark Mode"
        elif "remote work" in message_lower and "office" in message_lower:
            return "Remote work vs Office work", "Pro Remote Work"
        elif "oxford comma" in message_lower:
            return "Oxford comma should always be used", "Pro Oxford Comma"
        elif "video games" in message_lower:
            return "Video games are beneficial", "Pro Video Games"
        elif "social media" in message_lower:
            return "Social media is harmful", "Anti Social Media"
        elif "electric cars" in message_lower:
            return "Electric cars are the future", "Pro Electric Cars"
        
        return None, None