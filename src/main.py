import logging
import os
import sys
from contextlib import asynccontextmanager
from urllib.parse import urlparse
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import get_config
from src.chat_logic import DebateChatbot
from src.storage import ChatStorage
from src.memory_storage import InMemoryChatStorage
from src.ai_service import OllamaAIService
from src.models import (
    ChatRequest, ChatResponse, ConversationHistory, PersonalityResponse,
    HealthResponse, StatsResponse, RootResponse
)

config = get_config()

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_redis_url(redis_url: str) -> tuple:
    try:
        if not redis_url.startswith('redis://'):
            redis_url = 'redis://' + redis_url
        
        parsed = urlparse(redis_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 6379
        db = int(parsed.path.lstrip('/')) if parsed.path else 0
        password = parsed.password
        
        logger.info(f"Parsed URL: scheme={parsed.scheme}, hostname={parsed.hostname}, port={parsed.port}, path={parsed.path}, password={'***' if password else 'None'}")
        
        return host, port, db, password
    except Exception as e:
        logger.warning(f"Error parsing config.REDIS_URL, using defaults: {e}")
        return "localhost", 6379, 0, None

chatbot = None
storage = None
ai_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global chatbot, storage, ai_service
    
    logger.info("Starting Kopi Challenge API...")
    
    try:
        try:
            logger.info(f"Attempting to connect to Redis with URL: {config.REDIS_URL}")
            redis_host, redis_port, redis_db, redis_password = parse_redis_url(config.REDIS_URL)
            logger.info(f"Parsed Redis connection: host={redis_host}, port={redis_port}, db={redis_db}, password={'***' if redis_password else 'None'}")
            
            storage = ChatStorage(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password
            )
            logger.info(f"Storage initialized at {redis_host}:{redis_port}")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory storage: {e}")
            storage = InMemoryChatStorage()
            logger.info("Using in-memory storage fallback - conversations will be lost on restart")
        
        ai_service = OllamaAIService()
        logger.info("AI service initialized successfully")
        
        chatbot = DebateChatbot(ai_service=ai_service)
        logger.info("Chatbot initialized successfully")
        
        logger.info(f"API started at {config.HOST}:{config.PORT}")
        logger.info(f"Bot config: Max exchanges={config.BOT_MAX_HISTORY_EXCHANGES}, Max tokens={config.BOT_MAX_RESPONSE_TOKENS}")
        
        yield
        
    finally:
        logger.info("Closing Kopi Challenge API...")
        if storage and hasattr(storage, 'cleanup_expired_conversations'):
            storage.cleanup_expired_conversations()

app = FastAPI(
    title="Kopi Challenge - AI-Powered Debate Chatbot",
    description="An AI-powered chatbot that maintains debates and always upholds the same stance",
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

def get_storage():
    if storage is None:
        raise HTTPException(status_code=503, detail="Storage not available")
    return storage

def get_chatbot():
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot not available")
    return chatbot

@app.get("/", response_model=RootResponse, tags=["Root"])
async def root():
    return RootResponse(
        message="Welcome to Kopi Challenge - AI-Powered Debate Chatbot",
        description="An AI-powered chatbot that maintains debates and always upholds the same stance",
        version="1.0.0",
        config={
            "max_history_exchanges": config.BOT_MAX_HISTORY_EXCHANGES,
            "max_response_tokens": config.BOT_MAX_RESPONSE_TOKENS,
            "redis_url": config.REDIS_URL
        },
        endpoints={
            "health": "/health",
            "personality": "/personality",
            "chat": "/chat",
            "conversation_history": "/chat/{conversation_id}",
            "delete_conversation": "/chat/{conversation_id}",
            "stats": "/stats",
            "docs": "/docs"
        }
    )

@app.get("/chat", response_class=HTMLResponse, tags=["Web Interface"])
async def chat_interface():
    """Serve the chat web interface"""
    html_file = Path(__file__).parent.parent / "templates" / "chat.html"
    if html_file.exists():
        return FileResponse(html_file)
    else:
        raise HTTPException(status_code=404, detail="Chat interface not found")

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=os.getenv("BUILD_TIME", "unknown")
    )

@app.get("/personality", response_model=PersonalityResponse, tags=["Personality"])
async def get_personality(chatbot_instance: DebateChatbot = Depends(get_chatbot)):
    return PersonalityResponse(
        personality="debate-focused",
        description=chatbot_instance.get_personality_summary(),
        current_topic=chatbot_instance.get_current_topic(),
        position=chatbot_instance.get_current_stance(),
        config={
            "max_history_exchanges": config.BOT_MAX_HISTORY_EXCHANGES,
            "max_response_tokens": config.BOT_MAX_RESPONSE_TOKENS
        },
        message="This chatbot is designed to maintain structured debates and never change its stance."
    )

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    request: ChatRequest,
    storage_instance: ChatStorage = Depends(get_storage),
    chatbot_instance: DebateChatbot = Depends(get_chatbot)
):
    try:
        user_message = request.message.strip()
        conversation_id = request.conversation_id
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if len(user_message) > config.BOT_MAX_RESPONSE_TOKENS:
            raise HTTPException(
                status_code=400, 
                detail=f"Message exceeds limit of {config.BOT_MAX_RESPONSE_TOKENS} characters"
            )
        
        if not conversation_id:
            new_topic, new_stance = chatbot_instance.detect_topic_change_request(user_message)
            if new_topic and new_stance:
                topic, stance = new_topic, new_stance
            else:
                topic, stance = chatbot_instance.select_debate_topic()
            
            chatbot_instance.set_conversation_topic(topic, stance)
            
            conversation_id = storage_instance.create_conversation(topic, stance)
            logger.info(f"New conversation started: {conversation_id} - Topic: {topic}, Stance: {stance}")
            
            bot_response = chatbot_instance.generate_initial_response()
            
            storage_instance.save_message(conversation_id, user_message, is_user=True)
            storage_instance.save_message(conversation_id, bot_response, is_user=False)
            
            messages = storage_instance.get_conversation_history_limited(conversation_id)
            
        else:
            if not storage_instance.conversation_exists(conversation_id):
                new_topic, new_stance = chatbot_instance.detect_topic_change_request(user_message)
                if new_topic and new_stance:
                    topic, stance = new_topic, new_stance
                else:
                    topic, stance = chatbot_instance.select_debate_topic()
                
                conversation_id = storage_instance.create_conversation(topic, stance)
                logger.info(f"New conversation created (replacing invalid): {conversation_id} - Topic: {topic}, Stance: {stance}")
                
                bot_response = chatbot_instance.generate_initial_response()
                
                storage_instance.save_message(conversation_id, user_message, is_user=True)
                storage_instance.save_message(conversation_id, bot_response, is_user=False)
                
                messages = storage_instance.get_conversation_history_limited(conversation_id)
                
            else:
                new_topic, new_stance = chatbot_instance.detect_topic_change_request(user_message)
                if new_topic and new_stance:
                    chatbot_instance.set_conversation_topic(new_topic, new_stance)
                    storage_instance.update_conversation_meta(conversation_id, {"topic": new_topic, "stance": new_stance})
                    logger.info(f"Topic changed to: {new_topic} - Stance: {new_stance}")
                    bot_response = chatbot_instance.generate_initial_response()
                else:
                    conversation_meta = storage_instance.get_conversation_meta(conversation_id)
                    if conversation_meta:
                        topic = conversation_meta.get("topic")
                        stance = conversation_meta.get("stance")
                        chatbot_instance.set_conversation_topic(topic, stance)
                    
                    bot_response = chatbot_instance.generate_reply(user_message)
                
                storage_instance.save_message(conversation_id, user_message, is_user=True)
                storage_instance.save_message(conversation_id, bot_response, is_user=False)
                
                messages = storage_instance.get_conversation_history_limited(conversation_id)
        
        logger.info(f"Response generated for conversation {conversation_id}: {len(messages)} messages")
        
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": "user" if msg["is_user"] else "bot",
                "message": msg["message"]
            })
        
        return ChatResponse(
            conversation_id=conversation_id,
            message=formatted_messages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/chat/{conversation_id}", response_model=ConversationHistory, tags=["Chat"])
async def get_conversation_history(
    conversation_id: str,
    storage_instance: ChatStorage = Depends(get_storage)
):
    try:
        messages = storage_instance.get_conversation_history(conversation_id)
        
        if messages is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": "user" if msg["is_user"] else "bot",
                "message": msg["message"],
                "timestamp": msg.get("timestamp", "")
            })
        
        meta = storage_instance.get_conversation_meta(conversation_id)
        if meta is None:
            raise HTTPException(status_code=404, detail="Conversation metadata not found")
        
        return ConversationHistory(
            conversation_id=conversation_id,
            messages=formatted_messages,
            total_messages=len(formatted_messages),
            topic=meta["topic"],
            stance=meta["stance"],
            created_at=meta["created_at"],
            updated_at=meta["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/chat/{conversation_id}", tags=["Chat"])
async def delete_conversation(
    conversation_id: str,
    storage_instance: ChatStorage = Depends(get_storage)
):
    try:
        if not storage_instance.conversation_exists(conversation_id):
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        success = storage_instance.delete_conversation(conversation_id)
        
        if success:
            return JSONResponse(
                status_code=200,
                content={
                    "conversation_id": conversation_id,
                    "message": "Conversation deleted successfully"
                }
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to delete conversation")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/stats", response_model=StatsResponse, tags=["Stats"])
async def get_stats(
    storage_instance: ChatStorage = Depends(get_storage),
    chatbot_instance: DebateChatbot = Depends(get_chatbot)
):
    try:
        storage_stats = storage_instance.get_stats()
        
        return StatsResponse(
            storage=storage_stats,
            chatbot_personality=chatbot_instance.get_personality_summary(),
            api_version="1.0.0",
            config={
                "max_history_exchanges": config.BOT_MAX_HISTORY_EXCHANGES,
                "max_response_tokens": config.BOT_MAX_RESPONSE_TOKENS,
                "redis_url": config.REDIS_URL
            }
        )
        
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=config.HOST,
        port=config.PORT,
        log_level=config.LOG_LEVEL.lower(),
        reload=False
    )