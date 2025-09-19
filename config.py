#!/usr/bin/env python3
"""
Global Configuration for Kopi Challenge AI-Powered Debate Chatbot
Centralized configuration management for all components
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Global configuration class for the application"""
    
    DEFAULT_HOST = "0.0.0.0"
    DEFAULT_PORT = 8013
    HOST = os.getenv("HOST", DEFAULT_HOST)
    PORT = int(os.getenv("PORT", DEFAULT_PORT))
    BASE_URL = f"http://{HOST}:{PORT}"
    
    AI_MODEL = os.getenv("AI_MODEL", "llama3.1")
    AI_BASE_URL = os.getenv("AI_BASE_URL", "http://localhost:11434")
    AI_TIMEOUT = int(os.getenv("AI_TIMEOUT", "30"))
    AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "256"))
    
    BOT_MAX_HISTORY_EXCHANGES = int(os.getenv("BOT_MAX_HISTORY_EXCHANGES", "5"))
    BOT_MAX_RESPONSE_TOKENS = int(os.getenv("BOT_MAX_RESPONSE_TOKENS", "256"))
    
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    STORAGE_TTL_DAYS = int(os.getenv("STORAGE_TTL_DAYS", "7"))
    
    API_TITLE = "Kopi Challenge API"
    API_DESCRIPTION = "AI-Powered Debate Chatbot API"
    API_VERSION = "1.0.0"
    
    TEST_TIMEOUT = int(os.getenv("TEST_TIMEOUT", "30"))
    TEST_CONCURRENT_USERS = int(os.getenv("TEST_CONCURRENT_USERS", "5"))
    TEST_REQUESTS_PER_USER = int(os.getenv("TEST_REQUESTS_PER_USER", "3"))
    TEST_LOAD_DURATION = int(os.getenv("TEST_LOAD_DURATION", "60"))
    TEST_LOAD_RPS = int(os.getenv("TEST_LOAD_RPS", "1"))
    
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_base_url(cls, host: Optional[str] = None, port: Optional[int] = None) -> str:
        """Get base URL with optional host/port override"""
        if host is None:
            host = cls.HOST
        if port is None:
            port = cls.PORT
        return f"http://{host}:{port}"
    
    @classmethod
    def get_test_base_url(cls) -> str:
        """Get base URL for testing (always localhost)"""
        return f"http://localhost:{cls.PORT}"
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration values"""
        try:
            if not (1024 <= cls.PORT <= 65535):
                print(f"ERROR: Port {cls.PORT} is not in valid range (1024-65535)")
                return False
            
            if cls.AI_TIMEOUT <= 0:
                print(f"ERROR: AI timeout {cls.AI_TIMEOUT} must be positive")
                return False
            
            if cls.AI_MAX_TOKENS <= 0:
                print(f"ERROR: AI max tokens {cls.AI_MAX_TOKENS} must be positive")
                return False
            
            if cls.BOT_MAX_HISTORY_EXCHANGES <= 0:
                print(f"ERROR: Max history exchanges {cls.BOT_MAX_HISTORY_EXCHANGES} must be positive")
                return False
            
            return True
            
        except Exception as e:
            print(f"ERROR: Configuration validation failed: {e}")
            return False
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("Kopi Challenge Configuration:")
        print("=" * 40)
        print(f"Server: {cls.HOST}:{cls.PORT}")
        print(f"Base URL: {cls.BASE_URL}")
        print(f"AI Model: {cls.AI_MODEL}")
        print(f"AI Timeout: {cls.AI_TIMEOUT}s")
        print(f"AI Max Tokens: {cls.AI_MAX_TOKENS}")
        print(f"Bot Max History: {cls.BOT_MAX_HISTORY_EXCHANGES}")
        print(f"Redis URL: {cls.REDIS_URL}")
        print(f"Debug Mode: {cls.DEBUG}")
        print(f"Log Level: {cls.LOG_LEVEL}")
        print("=" * 40)

config = Config()

def get_config() -> Config:
    """Get global configuration instance"""
    return config

def validate_and_print_config() -> bool:
    """Validate configuration and print it"""
    if not config.validate_config():
        return False
    
    config.print_config()
    return True
