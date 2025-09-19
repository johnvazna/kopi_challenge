import logging
import random
from typing import Dict, List

from .ai_service import OllamaAIService

logger = logging.getLogger(__name__)

class DebateChatbot:
    """
    A chatbot that maintains a consistent stance in debates.
    Uses AI-powered responses while maintaining debate consistency.
    """
    
    def __init__(self, ai_service: OllamaAIService = None):
        """Initialize chatbot with debate topics and AI service"""
        # Initialize AI service
        self.ai_service = ai_service or OllamaAIService()
        
        # Test AI connection
        if not self.ai_service.test_connection():
            logger.warning("AI service connection failed, using fallback mode")
        self.debate_topics = {
            "Pineapple belongs on pizza": {
                "position": "Pro",
                "reasons": [
                    "Sweet-salty combination is a millennial culinary tradition",
                    "Pineapple adds freshness and contrast to cheese fat",
                    "It's a popular option in many cultures around the world"
                ],
                "analogies": [
                    "Like chocolate with salt, pineapple on pizza is the perfect combination of opposites",
                    "It's like mixing summer with winter in a single bite",
                    "Pineapple on pizza is like an unexpected hug: it surprises but comforts"
                ],
                "questions": [
                    "Don't you think diversity in cooking is what makes it exciting?",
                    "Have you really tried a well-prepared Hawaiian pizza?",
                    "Why limit culinary creativity with rigid rules?"
                ]
            },
            "Spaces vs Tabs": {
                "position": "Pro Tabs",
                "reasons": [
                    "Tabs are more efficient in terms of bytes",
                    "Each developer can configure their editor to display tabs as preferred",
                    "Tabs are the standard in many programming languages"
                ],
                "analogies": [
                    "Using spaces is like writing with pencil when you have a pen",
                    "Tabs are like shortcuts in life: they take you to the same place faster",
                    "Spaces vs Tabs is like discussing whether water should be blue or transparent"
                ],
                "questions": [
                    "Don't you prefer your code to be more compact and readable?",
                    "Why waste characters when you can use just one?",
                    "Have you considered the flexibility that tabs offer?"
                ]
            },
            "Dark mode is better than light mode": {
                "position": "Pro Dark Mode",
                "reasons": [
                    "Reduces eye fatigue during long work sessions",
                    "Consumes less battery on OLED devices",
                    "It's more elegant and modern visually"
                ],
                "analogies": [
                    "Light mode is like reading a book under direct sunlight",
                    "Dark mode is like driving at night: more relaxing for the eyes",
                    "Using light mode is like wearing sunglasses in a dark room"
                ],
                "questions": [
                    "Don't you get tired of bright light after hours of work?",
                    "Have you noticed the difference in your productivity with dark mode?",
                    "Why resist progress when it's healthier for your eyes?"
                ]
            },
            "Remote work is more productive": {
                "position": "Pro Remote Work",
                "reasons": [
                    "Eliminates time wasted on commuting",
                    "Allows a personalized and comfortable work environment",
                    "Reduces office distractions and improves concentration"
                ],
                "analogies": [
                    "Office work is like going to the supermarket when you can order delivery",
                    "Working from home is like having your own personal laboratory",
                    "The office is like a traditional classroom when you have access to online education"
                ],
                "questions": [
                    "Don't you value your time more than travel time?",
                    "Have you really measured your productivity in both environments?",
                    "Why insist on 20th century methods when we have 21st century technology?"
                ]
            },
            "Oxford comma should always be used": {
                "position": "Pro Oxford Comma",
                "reasons": [
                    "Eliminates ambiguity in complex lists",
                    "Maintains consistency with academic and formal style",
                    "It's clearer and more professional in written communication"
                ],
                "analogies": [
                    "Not using the Oxford comma is like not using traffic signs",
                    "The Oxford comma is like a seatbelt: better to have it and not need it",
                    "Omitting the Oxford comma is like leaving a door ajar"
                ],
                "questions": [
                    "Do you prefer clarity or confusion in your writing?",
                    "Don't you think precision in language is fundamental?",
                    "Why risk understanding to save one character?"
                ]
            },
            "Coffee is better than tea": {
                "position": "Pro Coffee",
                "reasons": [
                    "Coffee has a richer and more complex flavor",
                    "Provides a more immediate and lasting energy boost",
                    "Has a more passionate and social culture and ritual"
                ],
                "analogies": [
                    "Tea is like a gentle caress, coffee is like a strong hug",
                    "Tea is flavored water, coffee is a complete sensory experience",
                    "Drinking tea is like listening to classical music, drinking coffee is like going to a rock concert"
                ],
                "questions": [
                    "Don't you prefer to wake up completely instead of just waking up?",
                    "Have you experienced coffee culture in different countries?",
                    "Why settle for hot water when you can have a flavor explosion?"
                ]
            }
        }
        
        self.current_topic = random.choice(list(self.debate_topics.keys()))
        self.topic_info = self.debate_topics[self.current_topic]
        
        logger.info(f"Debate topic selected: {self.current_topic} - Stance: {self.topic_info['position']}")
    
    def pick_topic_and_stance(self) -> Dict[str, str]:
        """
        Randomly select a debate topic and return its stance.
        Returns a dictionary with 'topic' and 'stance'.
        """
        selected_topic = random.choice(list(self.debate_topics.keys()))
        selected_stance = self.debate_topics[selected_topic]["position"]
        
        logger.info(f"Topic selected: {selected_topic} - Stance: {selected_stance}")
        
        return {
            "topic": selected_topic,
            "stance": selected_stance
        }
    
    def set_topic_and_stance(self, topic: str, stance: str) -> bool:
        """
        Set a specific topic and stance for the debate.
        Returns True if set successfully, False if topic doesn't exist.
        """
        if topic in self.debate_topics:
            self.current_topic = topic
            self.topic_info = self.debate_topics[topic]
            logger.info(f"Topic set: {topic} - Stance: {stance}")
            return True
        else:
            logger.warning(f"Topic '{topic}' not found in available topics")
            return False
    
    def generate_reply(self, user_message: str, conversation_history: List[Dict] = None) -> str:
        """
        Generate a coherent chatbot response using AI.
        Returns a string with the AI-generated response.
        """
        try:
            # Handle invalid input
            if user_message is None:
                return f"My debate system is having problems, but my stance on **{self.current_topic}** remains unshakeable."
            
            if not isinstance(user_message, str):
                user_message = str(user_message)
            
            # Get current topic info
            topic = self.current_topic
            stance = self.topic_info["position"]
            
            # Generate AI response
            ai_response = self.ai_service.generate_response(
                topic=topic,
                stance=stance,
                user_message=user_message,
                conversation_history=conversation_history,
                is_initial=False
            )
            
            logger.info(f"Generated AI response for topic: {topic}, stance: {stance}")
            return ai_response
                
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return f"My debate system is having problems, but my stance on **{self.current_topic}** remains unshakeable."
    
    def get_topic_info(self) -> Dict[str, str]:
        """Return current debate topic information"""
        return {
            "topic": self.current_topic,
            "position": self.topic_info["position"],
            "reasons": self.topic_info["reasons"]
        }
    
    def generate_initial_response(self) -> str:
        """Generate bot's initial response using AI"""
        try:
            topic = self.current_topic
            stance = self.topic_info["position"]
            
            # Generate AI initial response
            ai_response = self.ai_service.generate_response(
                topic=topic,
                stance=stance,
                user_message="",  # Empty for initial response
                conversation_history=None,
                is_initial=True
            )
            
            logger.info(f"Generated AI initial response for topic: {topic}, stance: {stance}")
            return ai_response
            
        except Exception as e:
            logger.error(f"Error generating AI initial response: {e}")
            # Fallback to original method
            topic = self.current_topic
            position = self.topic_info["position"]
            reasons = self.topic_info["reasons"]
            
            response = f"Excellent! I have chosen to debate about: **{topic}**\n\n"
            response += f"My stance is **{position}**. I am completely convinced that:\n\n"
            
            for i, reason in enumerate(reasons, 1):
                response += f"{i}. {reason}\n"
            
            response += f"\n{random.choice(self.topic_info['analogies'])}\n\n"
            response += f"What do you think about {topic.lower()}? Can you give me arguments against it?"
            
            return response
    
    def generate_response(self, user_message: str, conversation_history: List[Dict] = None) -> str:
        """
        Generate a chatbot response using AI (alias for generate_reply for compatibility).
        """
        return self.generate_reply(user_message, conversation_history)
    
    def _is_asking_for_clarification(self, message: str) -> bool:
        """Detect if user is asking for clarification"""
        clarification_keywords = [
            "what do you mean", "explain", "i don't understand", "clarify"
        ]
        return any(keyword in message for keyword in clarification_keywords)
    
    def _is_challenging_position(self, message: str) -> bool:
        """Detect if user is challenging the stance"""
        challenge_keywords = [
            "you're wrong", "that's not true", "i disagree", "i don't agree"
        ]
        return any(keyword in message for keyword in challenge_keywords)
    
    def _is_asking_for_evidence(self, message: str) -> bool:
        """Detect if user is asking for evidence"""
        evidence_keywords = [
            "proof", "evidence", "source", "study", "research"
        ]
        return any(keyword in message for keyword in evidence_keywords)
    
    def _is_greeting(self, message: str) -> bool:
        """Detect if it's a greeting"""
        greeting_keywords = [
            "hello", "hi", "good morning", "good afternoon", "good evening",
            "hola", "buenos días", "buenas tardes", "buenas noches"
        ]
        return any(keyword in message for keyword in greeting_keywords)
    
    def _is_farewell(self, message: str) -> bool:
        """Detect if it's a farewell"""
        farewell_keywords = [
            "goodbye", "bye", "see you", "farewell"
        ]
        return any(keyword in message for keyword in farewell_keywords)
    
    def _clarify_position(self) -> str:
        """Clarify bot's stance"""
        response = f"My stance is clear: **{self.topic_info['position']}** on **{self.current_topic}**.\n\n"
        response += "There is no ambiguity in my position. I am completely convinced that:\n\n"
        
        for i, reason in enumerate(self.topic_info["reasons"], 1):
            response += f"{i}. {reason}\n"
        
        response += f"\n{random.choice(self.topic_info['analogies'])}\n\n"
        response += "What part of my argument is unclear to you?"
        
        return response
    
    def _defend_position(self, user_message: str) -> str:
        """Defend bot's stance"""
        response = f"I understand your point of view, but my stance on **{self.current_topic}** is unshakeable.\n\n"
        
        response += "I recognize that you have a different opinion, and that's valid in a debate.\n\n"
        
        response += f"However, I maintain my position **{self.topic_info['position']}** because:\n\n"
        
        selected_reasons = random.sample(self.topic_info["reasons"], min(3, len(self.topic_info["reasons"])))
        for i, reason in enumerate(selected_reasons, 1):
            response += f"{i}. {reason}\n"
        
        response += f"\n{random.choice(self.topic_info['analogies'])}\n\n"
        
        response += random.choice(self.topic_info["questions"])
        
        return response
    
    def _provide_evidence(self) -> str:
        """Provide evidence for the stance"""
        response = f"Excellent question! My stance **{self.topic_info['position']}** on **{self.current_topic}** is supported by:\n\n"
        
        for i, reason in enumerate(self.topic_info["reasons"], 1):
            response += f"{i}. {reason}\n"
        
        response += f"\n{random.choice(self.topic_info['analogies'])}\n\n"
        response += "Don't you think these arguments are convincing? What evidence do you have against?"
        
        return response
    
    def _greet_and_explain_topic(self) -> str:
        """Greet and explain debate topic"""
        return self.generate_initial_response()
    
    def _say_farewell(self) -> str:
        """Respond to farewells"""
        farewells = [
            f"Goodbye! Remember that my stance on **{self.current_topic}** remains **{self.topic_info['position']}**.",
            f"Adios. My conviction on **{self.current_topic}** is unshakeable.",
            f"See you. My stance **{self.topic_info['position']}** on **{self.current_topic}** will not change.",
            f"Until next time. My arguments on **{self.current_topic}** remain solid."
        ]
        return random.choice(farewells)
    
    def _generate_structured_response(self, user_message: str) -> str:
        """Generate a structured response following the rule-based format"""
        response = f"Regarding your comment on **{self.current_topic}**, my stance **{self.topic_info['position']}** remains firm.\n\n"
        
        response += "I appreciate your perspective, even if it's different from mine.\n\n"
        
        response += f"My position is clear: **{self.topic_info['position']}** on **{self.current_topic}**.\n\n"
        
        selected_reasons = random.sample(self.topic_info["reasons"], min(2, len(self.topic_info["reasons"])))
        for i, reason in enumerate(selected_reasons, 1):
            response += f"{i}. {reason}\n"
        
        response += f"\n{random.choice(self.topic_info['analogies'])}\n\n"
        
        response += random.choice(self.topic_info["questions"])
        
        return response
    
    def get_personality_summary(self) -> str:
        """Return a summary of the chatbot's personality"""
        ai_status = "AI-powered" if self.ai_service.test_connection() else "fallback mode"
        return (
            f"I am an {ai_status} debate-specialized chatbot that defends the **{self.topic_info['position']}** stance "
            f"on **{self.current_topic}**. I use advanced AI to generate dynamic, engaging responses while maintaining "
            "my unshakeable position. My responses include clear arguments, analogies, and questions to continue the debate. "
            "My stance is permanent and I will never change my opinion, regardless of the arguments presented."
        )
