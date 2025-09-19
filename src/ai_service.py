import logging
import requests
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class OllamaAIService:
    def __init__(self, model_name: str = None, base_url: str = None):
        from config import get_config
        config = get_config()
        self.model_name = model_name or config.AI_MODEL
        self.base_url = base_url or config.AI_BASE_URL
        self.api_url = f"{self.base_url}/api/generate"
        
        logger.info(f"Ollama AI Service initialized with model: {self.model_name}")
    
    def test_connection(self) -> bool:
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": "Hello",
                    "stream": False,
                    "options": {"num_predict": 1}
                },
                timeout=5
            )
            if response.status_code == 200:
                logger.info(f"Connection test successful. Model {self.model_name} is available.")
                return True
            else:
                logger.error(f"Ollama connection test failed with status {response.status_code}: {response.text}")
                return False
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Ollama connection error: {e}")
            return False
        except requests.exceptions.Timeout:
            logger.error("Ollama connection timed out.")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during Ollama connection test: {e}")
            return False
    
    def generate_response(self, topic: str, stance: str, user_message: str, 
                         conversation_history: Optional[List[Dict]] = None, 
                         is_initial: bool = False) -> str:
        try:
            if is_initial:
                prompt = self._build_initial_prompt(topic, stance)
            else:
                prompt = self._build_debate_prompt(topic, stance, user_message, conversation_history)
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "num_predict": 80,
                    "stop": ["USER:", "YOU:", "\n\n", "---"]
                }
            }
            
            logger.info(f"Generating response for topic: {topic}, stance: {stance}")
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "").strip()
                
                generated_text = self._clean_response(generated_text)
                
                logger.info(f"Generated response: {generated_text[:100]}...")
                return generated_text
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return self._get_fallback_response(topic, stance)
                
        except requests.exceptions.Timeout:
            logger.error("Ollama API request timed out.")
            return self._get_fallback_response(topic, stance)
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Ollama API connection error: {e}")
            return self._get_fallback_response(topic, stance)
        except Exception as e:
            logger.error(f"An unexpected error occurred during AI response generation: {e}")
            return self._get_fallback_response(topic, stance)
    
    def _build_initial_prompt(self, topic: str, stance: str) -> str:
        return f"""You are a passionate debate bot. Topic: {topic}. Your stance: {stance}.

Start the debate by:
1. Stating your {stance} position clearly
2. Give one strong argument
3. Ask a question to engage the user

Keep it under 60 words. Be enthusiastic and direct."""
    
    def _build_debate_prompt(self, topic: str, stance: str, user_message: str, 
                           conversation_history: Optional[List[Dict]] = None) -> str:
        context = ""
        if conversation_history:
            recent_messages = conversation_history[-4:]
            for msg in recent_messages:
                role = "User" if msg.get("is_user", False) else "Bot"
                context += f"{role}: {msg.get('message', '')}\n"
        
        return f"""You are a stubborn debate bot. Topic: {topic}. Your stance: {stance}.

Recent context:
{context}

User just said: {user_message}

Respond by:
1. Acknowledging their point briefly
2. Defending your {stance} position
3. Asking a question

Keep under 70 words. Stay passionate and never change your stance."""
    
    def _clean_response(self, response: str) -> str:
        prefixes_to_remove = [
            "I understand your point, but",
            "That's an interesting perspective, however",
            "I appreciate your view, but",
            "While I respect your opinion,",
            "You make a good point, but"
        ]
        
        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
                break
        
        if response and not response.endswith(('.', '!', '?')):
            response += "!"
        
        return response
    
    def _get_fallback_response(self, topic: str, stance: str) -> str:
        return f"I'm experiencing technical difficulties, but my stance on **{topic}** remains **{stance}**. Let's continue this debate!"