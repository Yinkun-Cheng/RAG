# AI Test Assistant Service

AI-powered test case generation service using LangChain and Claude 4.5 Sonnet.

## Features

- 🤖 Test case generation using Claude 4.5 Sonnet
- 🔍 RAG-based knowledge retrieval from historical PRDs and test cases
- 🎯 Multi-agent architecture (TestEngineerAgent + Subagents)
- 🛠️ Modular Skills and Tools system
- 📡 Streaming responses via Server-Sent Events (SSE)

## Architecture

```
ai-service/
├── main.py                 # FastAPI application entry point
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── api/               # API endpoints
│   ├── agent/             # Agent implementations
│   ├── skill/             # Skills (business capabilities)
│   ├── tool/              # Tools (atomic operations)
│   └── integration/       # External service integrations
├── tests/                 # Test files
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
└── .env.example          # Environment variables template
```

## Setup

### 1. Install Dependencies

```bash
cd ai-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Required environment variables:
- `BRCONNECTOR_API_KEY`: Your BRConnector API key
- `VOLCANO_EMBEDDING_API_KEY`: Your Volcano Engine API key
- `VOLCANO_EMBEDDING_ENDPOINT`: Volcano Engine endpoint URL

### 3. Run the Service

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

### 4. Access the API

- API Documentation: http://localhost:5000/docs
- Health Check: http://localhost:5000/health

## Docker

Build and run using Docker:

```bash
docker build -t ai-test-assistant .
docker run -p 5000:5000 --env-file .env ai-test-assistant
```

## Testing

Run tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app --cov-report=html
```

## API Endpoints

### Health Check
```
GET /health
```

### Generate Test Cases
```
POST /ai/generate
```

### Stream Chat Response
```
POST /ai/chat/stream
```

## Development

### Project Structure

- `app/agent/`: Agent implementations (TestEngineerAgent, Subagents)
- `app/skill/`: Skills (TestCaseGenerationSkill, ImpactAnalysisSkill, etc.)
- `app/tool/`: Tools (SearchPRDTool, GenerateTestCaseTool, etc.)
- `app/integration/`: External service clients (BRConnector, Weaviate, etc.)
- `app/api/`: FastAPI route handlers

### Adding New Features

1. Create new tools in `app/tool/`
2. Combine tools into skills in `app/skill/`
3. Register skills with agents in `app/agent/`
4. Add API endpoints in `app/api/`

## License

MIT
