# Kopi Challenge - AI-Powered Persistent Debate Chatbot

An AI-powered chatbot API that maintains debates and always upholds the same stance, regardless of arguments presented. The bot uses advanced AI (Ollama + Llama 3.1) to generate dynamic, engaging responses while maintaining its unshakeable position.

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose** (for Docker installation)
- **Python 3.11+** (for local installation)
- **Git** (to clone the repository)
- **Ollama** (for AI model - see installation below)

### Docker (Recommended)
```bash
git clone <repo-url>
cd kopi-challenge
make run
```

**Services available at:**
- 🌐 **API**: http://localhost:8000
- 📊 **Redis**: localhost:6379
- 📚 **API Docs**: http://localhost:8000/docs

### Local Installation
```bash
git clone <repo-url>
cd kopi-challenge

# Install Ollama (macOS)
brew install ollama
ollama pull llama3.1

# Or install Ollama (Linux)
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.1

# Start Ollama service
brew services start ollama  # macOS
# or: ollama serve  # Linux

# Setup Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start Redis (optional - will use in-memory storage if not available)
docker-compose up -d redis

# Run the API
python src/main.py
```

## 📱 Usage

### API Endpoints
- **POST** `/chat` - Send messages and debate
- **GET** `/chat/{id}` - Get conversation history
- **GET** `/ui` - Optional web interface

### How to Debate with the Bot

1. **Start a new conversation** by sending a message without `conversation_id`
2. **The bot will randomly select a topic** and take a stance
3. **Continue debating** by sending messages with the same `conversation_id`
4. **The bot will never change its opinion** - it's designed to be persistent

### Example API Request
```json
{
  "conversation_id": null,
  "message": "Let's debate about pineapple on pizza!"
}
```

### Testing Options

**Option 1: Postman/curl (Recommended for API testing)**
Test the endpoints directly with your preferred API client.

**Option 2: Web Interface**
Visit `http://localhost:8000/ui` for an interactive chat experience.

## 🛠️ Development

```bash
make test              # Run tests
make logs              # Show logs
make down              # Stop services
make clean             # Remove containers
make build             # Rebuild Docker image
make restart           # Restart services
```

## 🔧 Configuration

Copy `env.example` to `.env`:
```bash
cp env.example .env
```

Default values work out of the box, but you can customize:
- `PORT=8000`
- `HOST=0.0.0.0`
- `REDIS_URL=redis://localhost:6379/0`
- `BOT_MAX_HISTORY_EXCHANGES=5`
- `BOT_MAX_RESPONSE_TOKENS=256`

## 🏗️ Architecture

- **FastAPI** - Modern Python web framework
- **Ollama + Llama 3.1** - AI-powered response generation
- **Redis** - Conversation storage with 7-day TTL (fallback to in-memory)
- **Docker** - Complete containerization
- **AI Prompt Engineering** - Dynamic prompts for consistent debate responses
- **Fallback System** - Graceful degradation when AI service is unavailable

## 🤖 AI Features

### Dynamic Response Generation
- **AI-Powered**: Uses Ollama with Llama 3.1 for intelligent, contextual responses
- **Consistent Personality**: Advanced prompt engineering ensures the bot never changes its stance
- **Engaging Debates**: Generates analogies, examples, and rhetorical questions
- **Context Awareness**: Maintains conversation history for coherent responses

### Prompt Engineering
- **System Prompts**: Carefully crafted prompts that define the bot's stubborn personality
- **Context Injection**: Includes conversation history and current topic information
- **Response Formatting**: Structured prompts ensure consistent response format
- **Fallback Handling**: Graceful degradation when AI service is unavailable

### Performance Optimizations
- **Response Time**: Optimized for 10-15 second response times
- **Token Limits**: Balanced between quality and speed (150 tokens max)
- **Connection Testing**: Automatic AI service health checks
- **Error Handling**: Robust error handling with fallback responses

## 📝 License

MIT License - see [LICENSE](LICENSE) file.
