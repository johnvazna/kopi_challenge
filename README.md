# Kopi Challenge - AI-Powered Debate Chatbot

An intelligent debate chatbot powered by Ollama and Llama 3.1 that maintains persistent conversations and generates dynamic, context-aware responses.

## Features

- **AI-Powered Responses**: Uses Ollama with Llama 3.1 for dynamic, intelligent debate responses
- **Persistent Conversations**: Maintains conversation history with Redis or in-memory fallback
- **Multiple Debate Topics**: 10 predefined debate topics with intelligent stance selection
- **RESTful API**: FastAPI-based API with comprehensive endpoints
- **Professional UI**: Clean web interface for interactive debates

## Prerequisites

- Python 3.11+
- Ollama installed and running
- Llama 3.1 model downloaded

## Quick Start

### 1. Install Ollama and Model

```bash
# macOS
brew install ollama
ollama pull llama3.1
brew services start ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.1
ollama serve
```

### 2. Setup Project

```bash
git clone <repository-url>
cd kopi-challenge
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure the Application

```bash
# Quick setup with defaults
python setup_config.py

# Or customize configuration
python setup_config.py
# Choose option 2 for interactive setup
```

### 4. Start the Server

```bash
# Using the configuration script (recommended)
python start_server.py

# Or manually with custom port
PORT=8013 python src/main.py
```

### 5. Access Application

- **Web Interface**: http://localhost:8013/chat
- **API Documentation**: http://localhost:8013/docs
- **Health Check**: http://localhost:8013/health

## API Endpoints

- `POST /chat` - Start or continue a conversation
- `GET /chat/{conversation_id}` - Get conversation history
- `GET /personality` - Get bot personality and current topic
- `GET /health` - Health check
- `GET /stats` - System statistics

## Testing

```bash
# Run all tests (recommended)
python tests/run_all_tests.py

# Run individual test suites
python tests/test_comprehensive_system.py
python tests/test_integration_scenarios.py
python tests/test_load_performance.py

# Run manual tests
python tests/test_ai_manually.py
python tests/test_api_manually.py

# Run demo
python tests/demo_ai_integration.py

# Run formal tests
pytest tests/
```

## Architecture

- **FastAPI**: Web framework and API layer
- **Ollama + Llama 3.1**: AI model for response generation
- **Redis**: Conversation storage (with in-memory fallback)
- **AI Prompt Engineering**: Optimized prompts for debate personality

## Configuration

The application uses a centralized configuration system. All settings can be configured via environment variables or the `.env` file.

### Configuration Options

**Server Configuration:**
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8013)

**AI Service Configuration:**
- `AI_MODEL`: AI model name (default: llama3.1)
- `AI_BASE_URL`: Ollama service URL (default: http://localhost:11434)
- `AI_TIMEOUT`: AI request timeout in seconds (default: 30)
- `AI_MAX_TOKENS`: Maximum tokens per AI response (default: 256)

**Chatbot Configuration:**
- `BOT_MAX_HISTORY_EXCHANGES`: Maximum conversation history (default: 5)
- `BOT_MAX_RESPONSE_TOKENS`: Maximum response length (default: 256)

**Storage Configuration:**
- `REDIS_URL`: Redis connection string (default: redis://localhost:6379/0)
- `STORAGE_TTL_DAYS`: Conversation storage TTL in days (default: 7)

**Development Configuration:**
- `DEBUG`: Debug mode (default: false)
- `LOG_LEVEL`: Logging level (default: INFO)

### Quick Configuration

```bash
# Use default configuration
python setup_config.py

# Customize configuration
python setup_config.py
# Choose option 2 for interactive setup
```

## Development

The project uses a clean, modular architecture:

**Source Code (`src/`)**:
- `main.py`: FastAPI application and endpoints
- `chat_logic.py`: Core chatbot logic and AI integration
- `ai_service.py`: Ollama AI service wrapper
- `storage.py`: Redis storage implementation
- `memory_storage.py`: In-memory storage fallback
- `models.py`: Pydantic data models

**Testing (`tests/`)**:
- `test_ai_integration.py`: Formal AI integration tests
- `test_ai_manually.py`: Manual AI service tests
- `test_api_manually.py`: Manual API endpoint tests
- `demo_ai_integration.py`: AI integration demonstration
- `conftest.py`: Test configuration and fixtures

## License

MIT License - see LICENSE file for details.