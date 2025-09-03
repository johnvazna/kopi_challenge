# Kopi Challenge - Persistent Debate Chatbot

A chatbot API that maintains debates and always upholds the same stance, regardless of arguments presented. The bot is programmed to be consistent and never change its opinion.

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose** (for Docker installation)
- **Python 3.11+** (for local installation)
- **Git** (to clone the repository)

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

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
make install

# Start Redis (required)
docker-compose up -d redis
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
- **Redis** - Conversation storage with 7-day TTL
- **Docker** - Complete containerization
- **Rule-based engine** - Consistent debate responses

## 📝 License

MIT License - see [LICENSE](LICENSE) file.
