#!/usr/bin/env python3
"""
Start Server Script for Kopi Challenge AI-Powered Debate Chatbot
Uses global configuration for easy setup
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import get_config, validate_and_print_config

def main():
    """Start the server with configuration validation"""
    print("Starting Kopi Challenge AI-Powered Debate Chatbot")
    print("=" * 50)
    
    if not validate_and_print_config():
        print("Configuration validation failed!")
        sys.exit(1)
    
    try:
        from src.main import app
        import uvicorn
        
        config = get_config()
        
        print(f"\nStarting server on {config.HOST}:{config.PORT}")
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        uvicorn.run(
            app,
            host=config.HOST,
            port=config.PORT,
            log_level=config.LOG_LEVEL.lower()
        )
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
