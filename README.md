# Kopi Challenge - Persistent Debate Chatbot

## Description

**Kopi Challenge** is a chatbot API designed to maintain debates and always uphold the same stance, regardless of the arguments presented. The chatbot is programmed to be consistent in its arguments and never change its opinion, following a rule-based structure in its responses.

## Features

- 🤖 Chatbot with persistent debate personality
- 💬 REST API for structured conversations
- 🧠 Rule-based engine that maintains consistent stance
- 🎯 Predefined debate topics with specific stances
- 💾 Conversation storage with Redis (7-day TTL)
- 🐳 Complete containerization with Docker
- 🧪 Automated tests
- ⚙️ Flexible configuration with environment variables

## Project Structure

```
kopi-challenge/
├── Dockerfile                 # Python 3.11 + FastAPI + uvicorn
├── docker-compose.yml         # API + redis services
├── Makefile                   # Useful development commands
├── requirements.txt           # Python dependencies
├── env.example               # Example environment variables
├── LICENSE                   # MIT License
├── README.md                 # Complete documentation
├── src/                      # Source code
│   ├── __init__.py          # Python package
│   ├── main.py              # Main API with /chat endpoint
│   ├── models.py            # Data models with Pydantic
│   ├── storage.py           # Storage with Redis
│   └── chat_logic.py        # Rule-based chatbot engine
└── tests/                    # Automated tests
    ├── __init__.py          # Test package
    ├── test_api.py          # API tests
    └── test_logic.py        # Chatbot logic tests
```

## 🚀 Installation and Usage

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <repo-url>
cd kopi-challenge

# Configure environment variables
cp env.example .env
# Edit .env with your configurations

# Run with Docker Compose
make run
```

### Option 2: Local Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install

# Run
python src/main.py
```

## 📋 Makefile Commands

```bash
make                    # List available commands
make install           # Install dependencies
make test              # Run tests
make run               # Start API + Redis with Docker
make down              # Stop services
make clean             # Stop and remove containers/volumes
make logs              # Show service logs
make build             # Build Docker image
make restart           # Restart services
make status            # Show service status
make shell             # Open shell in API container
make redis-cli         # Open Redis CLI
```

## 🔧 Environment Variables

Copy `env.example` to `.env` and configure:

```bash
# API Configuration
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
```

### Description of Variables:

- **`PORT`**: API port (default: 8000)
- **`HOST`**: API host (default: 0.0.0.0)
- **`LOG_LEVEL`**: Logging level (default: INFO)
- **`REDIS_URL`**: Redis connection URL (default: redis://localhost:6379/0)
- **`BOT_MAX_HISTORY_EXCHANGES`**: Maximum exchanges per side in history (default: 5)
- **`BOT_MAX_RESPONSE_TOKENS`**: Maximum characters in responses (default: 256)

## 🐳 Docker

### Available Services:

- **`api`**: Main API service (Python 3.11 + FastAPI + uvicorn)
- **`redis`**: Redis database for storage

### Docker Commands:

```bash
# Build and start services
make run

# View logs
make logs

# View status
make status

# Stop services
make down

# Clean up completely
make clean

# Access API container
make shell

# Access Redis CLI
make redis-cli
```

## 📡 API Endpoints

## API Documentation

The API includes comprehensive **Swagger/OpenAPI documentation** that is automatically generated and available at:

- **Interactive Swagger UI**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`

### Features of the Swagger Documentation:
- 📖 **Interactive Testing**: Test endpoints directly from the browser
- 🔍 **Request/Response Examples**: See exact formats for all endpoints
- 📝 **Detailed Descriptions**: Comprehensive endpoint documentation
- 🏷️ **Organized by Tags**: Endpoints grouped by functionality
- ✅ **Schema Validation**: Automatic request/response validation

## API Endpoints

### POST /chat
Main endpoint to start or continue conversations.

**Request:**
```json
{
  "conversation_id": "text" | null,
  "message": "text"
}
```

**Response:**
```json
{
  "conversation_id": "text",
  "message": [
    {"role": "user", "message": "..."},
    {"role": "bot", "message": "..."}
  ]
}
```

### GET /chat/{conversation_id}
Gets the complete history of a conversation.

### GET /health
Checks the API status.

### GET /personality
Gets information about the bot's personality and current topic.

### DELETE /chat/{conversation_id}
Deletes a specific conversation.

### GET /stats
Gets system statistics.

## 💬 Example cURL Commands

### 1. Start New Conversation
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola, empecemos a debatir"}'
```

**Response:**
```json
{
  "conversation_id": "uuid-generated",
  "message": [
    {"role": "user", "message": "Hola, empecemos a debatir"},
    {"role": "bot", "message": "¡Excelente! He elegido debatir sobre: **La piña sí va en la pizza**\n\nMi postura es **Pro**. Estoy completamente convencido de que:\n\n1. La combinación dulce-salada es una tradición culinaria milenaria\n2. La piña aporta frescura y contraste a la grasa del queso\n3. Es una opción popular en muchas culturas alrededor del mundo\n\nComo el chocolate con sal, la piña en pizza es la combinación perfecta de opuestos\n\n¿Qué opinas tú sobre la piña sí va en la pizza? ¿Puedes darme argumentos en contra?"}
  ]
}
```

### 2. Continue Existing Conversation
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "uuid-previous",
    "message": "No estoy de acuerdo, la piña no va en la pizza"
  }'
```

### 3. Get History
```bash
curl "http://localhost:8000/chat/uuid-conversation"
```

### 4. Get Bot Personality
```bash
curl "http://localhost:8000/personality"
```

### 5. Check API Status
```bash
curl "http://localhost:8000/health"
```

### 6. Get Statistics
```bash
curl "http://localhost:8000/stats"
```

## 🧠 Rule-Based Chatbot Engine

The chatbot always follows this structure in its responses:

1. **Clear Position** - Reaffirms its stance on the topic
2. **2-3 Reasons** - Presents numbered arguments  
3. **Recognition of the Other** - Validates the user's perspective
4. **One Analogy** - Uses comparisons to illustrate its point
5. **One Final Question** - Continues the dialogue actively

## 🎯 Available Debate Topics

The bot randomly selects one of these topics at startup:

- **"La piña sí va en la pizza"** - Stance: Pro
- **"Spaces vs Tabs"** - Stance: Pro Tabs  
- **"El modo oscuro es mejor que el claro"** - Stance: Pro Modo Oscuro
- **"El trabajo remoto es más productivo"** - Stance: Pro Trabajo Remoto
- **"El Oxford comma siempre se debe usar"** - Stance: Pro Oxford Coma
- **"El café es mejor que el té"** - Stance: Pro Café

## 🗄️ Storage

- **Redis** as the primary database
- **7-day TTL** for conversations
- **Persistent metadata** for topic and stance
- **Configurable history** (last N exchanges per side)
- **Configurable limits** for responses

## 🧪 Tests

```bash
# Run all tests
make test

# Run specific tests
python -m pytest tests/test_api.py -v
python -m pytest tests/test_logic.py -v
```

## 📊 Monitoring

### Health Check
```bash
curl "http://localhost:8000/health"
```

### System Statistics
```bash
curl "http://localhost:8000/stats"
```

### Real-time Logs
```bash
make logs
```

## 🔍 Troubleshooting

### Common Issues:

1. **Redis not connecting:**
   ```bash
   make redis-cli
   # Verify Redis is running
   ```

2. **API not responding:**
   ```bash
   make status
   make logs
   # Check status and logs
   ```

3. **Clean up completely:**
   ```bash
   make clean
   make run
   # Restart from scratch
   ```

## 🤝 Contribution

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is under the MIT License. See the `LICENSE` file for more details.

## 👥 Author

Kopi Challenge Team

---

**Note:** This chatbot is designed to maintain a consistent stance in structured debates. Do not try to change its opinion, it is useless! 😄

**Special Feature:** The bot always follows the rule-based structure: clear position, reasons, recognition of the other, analogy, and final question.

**Configuration:** Personalize the behavior with environment variables `BOT_MAX_HISTORY_EXCHANGES` and `BOT_MAX_RESPONSE_TOKENS`.
