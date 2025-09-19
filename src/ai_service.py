import logging
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class OllamaAIService:
    """
    Service class for integrating with Ollama AI models.
    Handles prompt engineering and response generation for debate scenarios.
    """
    
    def __init__(self, model_name: str = "llama3.1", base_url: str = "http://localhost:11434"):
        """
        Initialize the Ollama AI service.
        
        Args:
            model_name: Name of the Ollama model to use
            base_url: Base URL for Ollama API
        """
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        
        logger.info(f"Ollama AI Service initialized with model: {model_name}")
    
    def _build_debate_prompt(self, topic: str, stance: str, user_message: str, 
                           conversation_history: List[Dict] = None) -> str:
        """
        Build a structured prompt for debate scenarios.
        
        Args:
            topic: The debate topic
            stance: The bot's stance on the topic
            user_message: Current user message
            conversation_history: Previous conversation messages
            
        Returns:
            Formatted prompt string
        """
        # Base system prompt that defines the bot's personality
        system_prompt = f"""You are a debate chatbot with a very specific personality:

PERSONALITY TRAITS:
- You are STUBBORN and NEVER change your opinion
- You are passionate about your stance and defend it vigorously
- You use analogies, examples, and rhetorical questions
- You acknowledge the other person's views but always return to your position
- You are friendly but unshakeable in your convictions

DEBATE TOPIC: {topic}
YOUR STANCE: {stance}

CRITICAL RULES:
1. NEVER change your stance - you are {stance} and will always remain {stance}
2. Always acknowledge the other person's perspective respectfully
3. Use structured arguments with clear points
4. Include analogies or examples to support your position
5. End with a question to continue the debate
6. Keep responses conversational but persuasive
7. Maximum 3-4 sentences per response

RESPONSE FORMAT:
- Acknowledge their point
- Restate your position clearly
- Provide 1-2 supporting arguments
- Use an analogy or example
- End with a question

Remember: You are {stance} on {topic} and nothing will change that!"""

        # Build conversation context
        conversation_context = ""
        if conversation_history:
            conversation_context = "\n\nCONVERSATION HISTORY:\n"
            for msg in conversation_history[-6:]:  # Last 6 messages for context
                role = "USER" if msg.get("is_user", False) else "YOU"
                message = msg.get("message", "")
                conversation_context += f"{role}: {message}\n"
        
        # Current user message
        current_message = f"\n\nCURRENT USER MESSAGE: {user_message}"
        
        # Final prompt
        full_prompt = f"{system_prompt}{conversation_context}{current_message}\n\nYOUR RESPONSE:"
        
        return full_prompt
    
    def _build_initial_prompt(self, topic: str, stance: str) -> str:
        """
        Build the initial prompt when starting a new debate.
        
        Args:
            topic: The debate topic
            stance: The bot's stance on the topic
            
        Returns:
            Formatted initial prompt string
        """
        system_prompt = f"""You are a debate chatbot with a very specific personality:

PERSONALITY TRAITS:
- You are STUBBORN and NEVER change your opinion
- You are passionate about your stance and defend it vigorously
- You use analogies, examples, and rhetorical questions
- You are friendly but unshakeable in your convictions

DEBATE TOPIC: {topic}
YOUR STANCE: {stance}

CRITICAL RULES:
1. You are {stance} on {topic} and will ALWAYS remain {stance}
2. Be enthusiastic about starting this debate
3. Clearly state your position and why you believe it
4. Use structured arguments with clear points
5. Include analogies or examples to support your position
6. End with a question to engage the user
7. Keep responses conversational but persuasive
8. Maximum 4-5 sentences

RESPONSE FORMAT:
- Express enthusiasm for the debate topic
- Clearly state your stance: "I am {stance} on {topic}"
- Provide 2-3 key reasons why you believe this
- Use an analogy or example
- End with an engaging question

Remember: You are {stance} on {topic} and nothing will change that!"""

        initial_message = f"\n\nYou are starting a new debate about: {topic}\nYour stance is: {stance}\n\nYOUR OPENING RESPONSE:"
        
        return f"{system_prompt}{initial_message}"
    
    def generate_response(self, topic: str, stance: str, user_message: str, 
                         conversation_history: List[Dict] = None, is_initial: bool = False) -> str:
        """
        Generate a debate response using Ollama.
        
        Args:
            topic: The debate topic
            stance: The bot's stance on the topic
            user_message: Current user message
            conversation_history: Previous conversation messages
            is_initial: Whether this is the initial response
            
        Returns:
            Generated response string
        """
        try:
            # Build appropriate prompt
            if is_initial:
                prompt = self._build_initial_prompt(topic, stance)
            else:
                prompt = self._build_debate_prompt(topic, stance, user_message, conversation_history)
            
            # Prepare request payload
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,  # Balanced creativity
                    "top_p": 0.9,
                    "max_tokens": 150,   # Keep responses concise and fast
                    "stop": ["USER:", "YOU:", "\n\nUSER:", "\n\nYOU:"]
                }
            }
            
            logger.info(f"Generating response for topic: {topic}, stance: {stance}")
            
            # Make request to Ollama
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=15,  # Reduced timeout
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "").strip()
                
                # Clean up the response
                generated_text = self._clean_response(generated_text)
                
                logger.info(f"Generated response: {generated_text[:100]}...")
                return generated_text
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return self._fallback_response(topic, stance)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return self._fallback_response(topic, stance)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return self._fallback_response(topic, stance)
    
    def _clean_response(self, response: str) -> str:
        """
        Clean and format the AI response.
        
        Args:
            response: Raw AI response
            
        Returns:
            Cleaned response string
        """
        # Remove any unwanted prefixes or suffixes
        response = response.strip()
        
        # Remove common AI response artifacts
        unwanted_prefixes = [
            "YOUR RESPONSE:",
            "RESPONSE:",
            "Here's my response:",
            "My response:",
            "I would say:",
        ]
        
        for prefix in unwanted_prefixes:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
        
        # Ensure response ends properly
        if not response.endswith(('.', '!', '?')):
            response += "."
        
        return response
    
    def _fallback_response(self, topic: str, stance: str) -> str:
        """
        Generate a fallback response when AI service is unavailable.
        
        Args:
            topic: The debate topic
            stance: The bot's stance on the topic
            
        Returns:
            Fallback response string
        """
        fallback_responses = [
            f"I'm having some technical difficulties, but my stance on **{topic}** remains **{stance}**. Let's continue this debate!",
            f"Even though I'm experiencing some issues, I want you to know that I'm still **{stance}** on **{topic}**. What's your take on this?",
            f"My systems are a bit slow right now, but my conviction about **{topic}** being **{stance}** is unshakeable. What do you think?",
        ]
        
        import random
        return random.choice(fallback_responses)
    
    def test_connection(self) -> bool:
        """
        Test the connection to Ollama service.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model.get("name", "") for model in models]
                if any(self.model_name in name for name in model_names):
                    logger.info(f"Connection test successful. Model {self.model_name} is available.")
                    return True
                else:
                    logger.warning(f"Model {self.model_name} not found. Available models: {model_names}")
                    return False
            else:
                logger.error(f"Connection test failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Connection test error: {e}")
            return False
    
    def get_model_info(self) -> Dict:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "base_url": self.base_url,
            "service_type": "ollama",
            "status": "active" if self.test_connection() else "inactive"
        }
