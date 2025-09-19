#!/usr/bin/env python3
"""
Configuration Setup Script for Kopi Challenge AI-Powered Debate Chatbot
Helps users configure the application easily
"""

from pathlib import Path

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print(".env file already exists")
        return True
    
    if not env_example.exists():
        print("env.example file not found")
        return False
    
    with open(env_example, 'r') as src, open(env_file, 'w') as dst:
        dst.write(src.read())
    
    print("Created .env file from template")
    return True

def interactive_config():
    """Interactive configuration setup"""
    print("Kopi Challenge Configuration Setup")
    print("=" * 40)
    
    config = {}
    
    print("\n1. Server Configuration:")
    config['HOST'] = input("Host (default: 0.0.0.0): ").strip() or "0.0.0.0"
    config['PORT'] = input("Port (default: 8013): ").strip() or "8013"
    
    print("\n2. AI Configuration:")
    config['AI_MODEL'] = input("AI Model (default: llama3.1): ").strip() or "llama3.1"
    config['AI_BASE_URL'] = input("AI Base URL (default: http://localhost:11434): ").strip() or "http://localhost:11434"
    config['AI_TIMEOUT'] = input("AI Timeout in seconds (default: 30): ").strip() or "30"
    config['AI_MAX_TOKENS'] = input("AI Max Tokens (default: 256): ").strip() or "256"
    
    print("\n3. Chatbot Configuration:")
    config['BOT_MAX_HISTORY_EXCHANGES'] = input("Max History Exchanges (default: 5): ").strip() or "5"
    config['BOT_MAX_RESPONSE_TOKENS'] = input("Max Response Tokens (default: 256): ").strip() or "256"
    
    print("\n4. Storage Configuration:")
    config['REDIS_URL'] = input("Redis URL (default: redis://localhost:6379/0): ").strip() or "redis://localhost:6379/0"
    config['STORAGE_TTL_DAYS'] = input("Storage TTL in days (default: 7): ").strip() or "7"
    
    print("\n5. Development Configuration:")
    config['DEBUG'] = input("Debug mode (true/false, default: false): ").strip().lower() or "false"
    config['LOG_LEVEL'] = input("Log Level (DEBUG/INFO/WARNING/ERROR, default: INFO): ").strip().upper() or "INFO"
    
    return config

def save_config(config):
    """Save configuration to .env file"""
    env_file = Path(".env")
    
    with open(env_file, 'w') as f:
        f.write("HOST={}\n".format(config['HOST']))
        f.write("PORT={}\n".format(config['PORT']))
        f.write("AI_MODEL={}\n".format(config['AI_MODEL']))
        f.write("AI_BASE_URL={}\n".format(config['AI_BASE_URL']))
        f.write("AI_TIMEOUT={}\n".format(config['AI_TIMEOUT']))
        f.write("AI_MAX_TOKENS={}\n".format(config['AI_MAX_TOKENS']))
        f.write("BOT_MAX_HISTORY_EXCHANGES={}\n".format(config['BOT_MAX_HISTORY_EXCHANGES']))
        f.write("BOT_MAX_RESPONSE_TOKENS={}\n".format(config['BOT_MAX_RESPONSE_TOKENS']))
        f.write("REDIS_URL={}\n".format(config['REDIS_URL']))
        f.write("STORAGE_TTL_DAYS={}\n".format(config['STORAGE_TTL_DAYS']))
        f.write("DEBUG={}\n".format(config['DEBUG']))
        f.write("LOG_LEVEL={}\n".format(config['LOG_LEVEL']))
    
    print("Configuration saved to .env file")

def main():
    """Main configuration setup"""
    print("Kopi Challenge Configuration Setup")
    print("=" * 40)
    
    env_file = Path(".env")
    if env_file.exists():
        response = input(".env file already exists. Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("Configuration setup cancelled")
            return
    
    print("\nChoose setup method:")
    print("1. Use default configuration (quick setup)")
    print("2. Interactive configuration (custom setup)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        if create_env_file():
            print("Default configuration created")
            print("\nTo customize, edit the .env file or run this script again")
        else:
            print("Failed to create default configuration")
    elif choice == "2":
        config = interactive_config()
        save_config(config)
        print("Custom configuration created")
    else:
        print("Invalid choice")
        return
    
    print("\nNext steps:")
    print("1. Make sure Ollama is running: ollama serve")
    print("2. Pull the AI model: ollama pull llama3.1")
    print("3. Start the server: python start_server.py")
    print("4. Run tests: python tests/run_all_tests.py")

if __name__ == "__main__":
    main()
