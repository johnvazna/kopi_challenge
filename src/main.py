import logging
import os
from contextlib import asynccontextmanager
from urllib.parse import urlparse

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from src.chat_logic import DebateChatbot
from src.storage import ChatStorage
from src.models import (
    ChatRequest, ChatResponse, ConversationHistory, PersonalityResponse,
    HealthResponse, StatsResponse, RootResponse
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
BOT_MAX_HISTORY_EXCHANGES = int(os.getenv("BOT_MAX_HISTORY_EXCHANGES", 5))
BOT_MAX_RESPONSE_TOKENS = int(os.getenv("BOT_MAX_RESPONSE_TOKENS", 256))

def parse_redis_url(redis_url: str) -> tuple:
    """Parse Redis URL and return host, port, db"""
    try:
        parsed = urlparse(redis_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 6379
        db = int(parsed.path.lstrip('/')) if parsed.path else 0
        return host, port, db
    except Exception as e:
        logger.warning(f"Error parsing REDIS_URL, using defaults: {e}")
        return "localhost", 6379, 0

chatbot = None
storage = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    global chatbot, storage
    
    logger.info("Starting Kopi Challenge API...")
    
    try:
        # Try to connect to Redis, but don't fail if unavailable
        try:
            redis_host, redis_port, redis_db = parse_redis_url(REDIS_URL)
            storage = ChatStorage(
                host=redis_host,
                port=redis_port,
                db=redis_db
            )
            logger.info(f"Storage initialized at {redis_host}:{redis_port}")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory storage: {e}")
            storage = None
        
        chatbot = DebateChatbot()
        logger.info("Chatbot initialized successfully")
        
        logger.info(f"API started at {HOST}:{PORT}")
        logger.info(f"Bot config: Max exchanges={BOT_MAX_HISTORY_EXCHANGES}, Max tokens={BOT_MAX_RESPONSE_TOKENS}")
        
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        raise
    
    yield
    
    logger.info("Closing Kopi Challenge API...")
    if storage:
        try:
            storage.cleanup_expired_conversations()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

app = FastAPI(
    title="Kopi Challenge API",
    description="API for a persistent debate chatbot that maintains its stance regardless of arguments presented.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# No templates needed for static HTML

def get_storage() -> ChatStorage:
    """Dependency to get storage instance"""
    if storage is None:
        raise HTTPException(status_code=503, detail="Storage not available")
    return storage

def get_chatbot() -> DebateChatbot:
    """Dependency to get chatbot instance"""
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not available")
    return chatbot

@app.get("/", response_model=RootResponse, tags=["Information"])
async def root():
    """
    Root endpoint with API information and available endpoints.
    
    Returns basic information about the API and lists all available endpoints.
    """
    return RootResponse(
        message="Welcome to Kopi Challenge!",
        description="API for a stubborn chatbot that never changes its opinion",
        version="1.0.0",
        config={
            "max_history_exchanges": BOT_MAX_HISTORY_EXCHANGES,
            "max_response_tokens": BOT_MAX_RESPONSE_TOKENS
        },
        endpoints={
            "POST /chat": "Start or continue a conversation",
            "GET /chat/{conversation_id}": "Get conversation history",
            "DELETE /chat/{conversation_id}": "Delete a conversation",
            "GET /health": "Check API status",
            "GET /personality": "Get chatbot personality description",
            "GET /stats": "Get system statistics"
        }
    )

@app.get("/ui", tags=["UI"])
async def chat_ui():
    """
    Chat UI interface for testing the chatbot.
    
    Provides a ChatGPT-style web interface to interact with the debate chatbot.
    """
    return FileResponse("templates/chat.html")

@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
async def health_check():
    """
    Check API health status.
    
    Returns the current health status of the API and its version.
    Useful for monitoring and load balancers.
    """
    try:
        if storage:
            storage.get_stats()
        
        return HealthResponse(
            status="healthy",
            version="1.0.0"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/personality", response_model=PersonalityResponse, tags=["Chatbot"])
async def get_personality(chatbot_instance: DebateChatbot = Depends(get_chatbot)):
    """
    Get chatbot personality information.
    
    Returns details about the chatbot's current personality, including:
    - Current debate topic
    - Bot's stance on the topic
    - Personality description
    - Configuration settings
    """
    topic_info = chatbot_instance.get_topic_info()
    return PersonalityResponse(
        personality="debate-focused",
        description=chatbot_instance.get_personality_summary(),
        current_topic=topic_info["topic"],
        position=topic_info["position"],
        config={
            "max_history_exchanges": BOT_MAX_HISTORY_EXCHANGES,
            "max_response_tokens": BOT_MAX_RESPONSE_TOKENS
        },
        message="This chatbot is designed to maintain structured debates and never change its stance."
    )

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    request: ChatRequest,
    storage_instance: ChatStorage = Depends(get_storage),
    chatbot_instance: DebateChatbot = Depends(get_chatbot)
):
    """
    Main chat endpoint that handles new and existing conversations.
    
    This endpoint allows you to:
    - Start a new debate by sending a message without conversation_id
    - Continue an existing debate by providing the conversation_id
    
    The bot will:
    - Randomly select a debate topic for new conversations
    - Maintain its stance throughout the entire conversation
    - Provide structured, persuasive responses
    - Never change its opinion regardless of arguments presented
    
    **Example Usage:**
    - Start new debate: `{"message": "Hello, let's debate!"}`
    - Continue debate: `{"conversation_id": "uuid", "message": "I disagree with you"}`
    """
    try:
        user_message = request.message
        conversation_id = request.conversation_id
        
        if not user_message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if len(user_message) > BOT_MAX_RESPONSE_TOKENS:
            raise HTTPException(
                status_code=400, 
                detail=f"Message exceeds limit of {BOT_MAX_RESPONSE_TOKENS} characters"
            )
        
        if not conversation_id:
            topic_stance = chatbot_instance.pick_topic_and_stance()
            topic = topic_stance["topic"]
            stance = topic_stance["stance"]
            
            conversation_id = storage_instance.create_conversation(topic, stance)
            logger.info(f"New conversation started: {conversation_id} - Topic: {topic}, Stance: {stance}")
            
            bot_response = chatbot_instance.generate_initial_response()
            
            storage_instance.save_message(conversation_id, user_message, is_user=True)
            storage_instance.save_message(conversation_id, bot_response, is_user=False)
            
            messages = storage_instance.get_conversation_history_limited(conversation_id)
            
        else:
            if not storage_instance.conversation_exists(conversation_id):
                topic_stance = chatbot_instance.pick_topic_and_stance()
                topic = topic_stance["topic"]
                stance = topic_stance["stance"]
                
                conversation_id = storage_instance.create_conversation(topic, stance)
                logger.info(f"New conversation created (replacing invalid): {conversation_id} - Topic: {topic}, Stance: {stance}")
                
                bot_response = chatbot_instance.generate_initial_response()
                
                storage_instance.save_message(conversation_id, user_message, is_user=True)
                storage_instance.save_message(conversation_id, bot_response, is_user=False)
                
                messages = storage_instance.get_conversation_history_limited(conversation_id)
                
            else:
                bot_response = chatbot_instance.generate_reply(user_message)
                
                storage_instance.save_message(conversation_id, user_message, is_user=True)
                storage_instance.save_message(conversation_id, bot_response, is_user=False)
                
                messages = storage_instance.get_conversation_history_limited(conversation_id)
        
        logger.info(f"Response generated for conversation {conversation_id}: {len(messages)} messages")
        
        return ChatResponse(
            conversation_id=conversation_id,
            message=messages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/chat/{conversation_id}", response_model=ConversationHistory, tags=["Chat"])
async def get_chat_history(
    conversation_id: str,
    storage_instance: ChatStorage = Depends(get_storage)
):
    """
    Get complete conversation history.
    
    Retrieves all messages in a specific conversation, including:
    - Complete message history
    - Conversation metadata (topic, stance, timestamps)
    - Configuration settings
    """
    try:
        messages = storage_instance.get_conversation_history(conversation_id)
        
        if messages is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": "user" if msg["is_user"] else "bot",
                "message": msg["message"],
                "timestamp": msg["timestamp"]
            })
        
        meta = storage_instance.get_conversation_meta(conversation_id)
        
        return ConversationHistory(
            conversation_id=conversation_id,
            messages=formatted_messages,
            total_messages=len(messages),
            topic=meta["topic"] if meta else None,
            stance=meta["stance"] if meta else None,
            created_at=meta["created_at"] if meta else None,
            updated_at=meta["updated_at"] if meta else None,
            config={
                "max_history_exchanges": BOT_MAX_HISTORY_EXCHANGES,
                "max_response_tokens": BOT_MAX_RESPONSE_TOKENS
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation history {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/chat/{conversation_id}", response_model=dict, tags=["Chat"])
async def delete_chat_conversation(
    conversation_id: str,
    storage_instance: ChatStorage = Depends(get_storage)
):
    """
    Delete a chat conversation.
    
    Permanently removes a conversation and all its messages from storage.
    This action cannot be undone.
    """
    try:
        success = storage_instance.delete_conversation(conversation_id)
        
        if success:
            return {
                "message": f"Conversation {conversation_id} deleted successfully",
                "conversation_id": conversation_id
            }
        else:
            raise HTTPException(status_code=404, detail="Conversation not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/stats", response_model=StatsResponse, tags=["Monitoring"])
async def get_stats(storage_instance: ChatStorage = Depends(get_storage)):
    """
    Get system statistics.
    
    Returns comprehensive system information including:
    - Storage statistics (active conversations, total messages)
    - Chatbot personality information
    - API configuration details
    - System health metrics
    """
    try:
        storage_stats = storage_instance.get_stats()
        return StatsResponse(
            storage=storage_stats,
            chatbot_personality="debate-focused",
            api_version="1.0.0",
            config={
                "max_history_exchanges": BOT_MAX_HISTORY_EXCHANGES,
                "max_response_tokens": BOT_MAX_RESPONSE_TOKENS
            }
        )
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail="Error getting statistics")

@app.get("/examples", response_model=dict, tags=["Information"])
async def get_examples():
    """
    Get example requests and responses for the API.
    
    Provides practical examples of how to use each endpoint,
    including request formats and expected responses.
    """
    return {
        "chat_examples": {
            "start_new_debate": {
                "request": {
                    "message": "Hello, let's start debating about pineapple on pizza!"
                },
                "response": {
                    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                    "message": [
                        {"role": "user", "message": "Hello, let's start debating about pineapple on pizza!"},
                        {"role": "bot", "message": "Excellent! I have chosen to debate about: **Pineapple on Pizza**\n\nMy stance is **Pro Pineapple**. I am completely convinced that:\n\n1. Pineapple adds a sweet contrast to savory flavors\n2. It's a traditional Hawaiian pizza ingredient\n3. The combination creates a unique taste experience\n\nPineapple on pizza is like having dessert with your meal\n\nWhat do you think about pineapple on pizza? Can you give me arguments against it?"}
                    ]
                }
            },
            "continue_debate": {
                "request": {
                    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                    "message": "I think pineapple doesn't belong on pizza. It's too sweet!"
                },
                "response": {
                    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                    "message": [
                        {"role": "user", "message": "Hello, let's start debating about pineapple on pizza!"},
                        {"role": "bot", "message": "Excellent! I have chosen to debate about: **Pineapple on Pizza**\n\nMy stance is **Pro Pineapple**. I am completely convinced that:\n\n1. Pineapple adds a sweet contrast to savory flavors\n2. It's a traditional Hawaiian pizza ingredient\n3. The combination creates a unique taste experience\n\nPineapple on pizza is like having dessert with your meal\n\nWhat do you think about pineapple on pizza? Can you give me arguments against it?"},
                        {"role": "user", "message": "I think pineapple doesn't belong on pizza. It's too sweet!"},
                        {"role": "bot", "message": "I understand your point of view, but my stance on **Pineapple on Pizza** is unshakeable.\n\nI recognize that you have a different opinion, and that's valid in a debate.\n\nHowever, I maintain my position **Pro Pineapple** because:\n\n1. Pineapple adds a sweet contrast to savory flavors\n2. It's a traditional Hawaiian pizza ingredient\n\nPineapple on pizza is like having dessert with your meal\n\nDon't you think the sweet-savory combination is what makes it special?"}
                    ]
                }
            }
        },
        "available_topics": [
            "Pineapple on Pizza (Pro Pineapple)",
            "Spaces vs Tabs (Pro Tabs)", 
            "Dark Mode vs Light Mode (Pro Dark Mode)",
            "Remote Work vs Office Work (Pro Remote Work)"
        ],
        "response_format": {
            "conversation_id": "UUID string",
            "message": "Array of message objects with role and message fields"
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return {
        "error": "Internal server error",
        "detail": "An unexpected error occurred"
    }

if __name__ == "__main__":
    logging.getLogger().setLevel(getattr(logging, LOG_LEVEL.upper()))
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level=LOG_LEVEL.lower()
    )
