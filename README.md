# StockBot - AI-Powered Stock Market Assistant

An intelligent chatbot that answers stock market queries using **Retrieval Augmented Generation (RAG)**. Users can choose their preferred LLM provider — Google Gemini, Anthropic Claude, or OpenAI GPT — and bring their own API key.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![React](https://img.shields.io/badge/React-18-61DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)

## Features

- **Multi-LLM Support** — Switch between Google Gemini, Anthropic Claude, and OpenAI GPT from the UI
- **Bring Your Own Key** — Enter your API key, test the connection, and start chatting
- **RAG Pipeline** — Answers grounded in real financial documents via vector similarity search
- **Conversation Memory** — Maintains context across follow-up questions (last 3 turns)
- **Follow-up Suggestions** — Every answer includes logical follow-up questions
- **Request Logging** — Structured logging with rotation for all API requests and LLM interactions

## Architecture

```
React Frontend (port 3000)
    │
    ├── LLM Settings Modal (provider/model/key selection)
    └── Chat Interface
            │
            ▼
FastAPI Backend (port 8000)
    │
    ├── /llm/providers    → Available LLM providers & models
    ├── /llm/test         → Test API key connection
    ├── /answer/          → RAG pipeline + LLM response
    └── /health           → Health check
            │
            ▼
    ┌───────────────┐     ┌──────────────────┐
    │ AstraDB       │     │ LLM Provider     │
    │ Vector Store  │     │ (Gemini/Claude/  │
    │ (embeddings)  │     │  GPT)            │
    └───────────────┘     └──────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Material UI, Axios |
| **Backend** | Python, FastAPI, LangChain |
| **LLMs** | Google Gemini Pro, Anthropic Claude, OpenAI GPT |
| **Embeddings** | HuggingFace `hkunlp/instructor-large` |
| **Vector DB** | DataStax AstraDB |
| **Deployment** | Docker, Docker Compose |

## Project Structure

```
StockBot/
├── server/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # App entry, CORS, request logging middleware
│   │   ├── config.py          # Environment variable management
│   │   ├── routes.py          # API endpoints
│   │   ├── logger.py          # Centralized logging (file + console)
│   │   └── services/
│   │       ├── rag.py         # RAG pipeline (embeddings, vector search, QA chain)
│   │       ├── llm_provider.py # Multi-LLM factory (Google/Anthropic/OpenAI)
│   │       └── memory.py      # Conversation memory
│   ├── scripts/
│   │   └── upload.py          # PDF ingestion into AstraDB
│   ├── data/pdfs/             # Knowledge base PDFs
│   ├── Dockerfile
│   └── requirements.txt
│
├── client/                    # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── LLMSettings.jsx  # LLM provider/model/key selector
│   │   │   ├── BotResponse.jsx  # Typewriter response animation
│   │   │   └── ...
│   │   ├── services/
│   │   │   └── api.js         # API client with LLM config support
│   │   └── pages/
│   │       └── Home.jsx       # Main chat interface
│   ├── Dockerfile
│   └── .env.example
│
├── notebooks/                 # Research notebooks (Gemini & Llama 2)
├── docker-compose.yml
└── .env.example
```

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- DataStax AstraDB account (for vector storage)
- At least one LLM API key (Google/Anthropic/OpenAI)

### Backend Setup

```bash
cd server
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your AstraDB credentials and (optionally) a default Google API key

# Ingest PDFs into the vector database (one-time)
python scripts/upload.py

# Start the server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd client
npm install

# Configure API URL
cp .env.example .env
# Edit .env if backend is not on localhost:8000

npm start
```

### Docker

```bash
docker-compose up
```

The frontend will be at `http://localhost:3000` and the backend at `http://localhost:8000`.

## Environment Variables

### Backend (`server/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | No | Default Google Gemini API key (users can provide their own) |
| `ASTRA_DB_APPLICATION_TOKEN` | Yes | DataStax AstraDB authentication token |
| `ASTRA_DB_API_ENDPOINT` | Yes | DataStax AstraDB API endpoint URL |
| `CORS_ORIGINS` | No | Comma-separated allowed origins (default: `http://localhost:3000`) |
| `LOG_LEVEL` | No | Logging level: DEBUG, INFO, WARNING, ERROR (default: `INFO`) |

### Frontend (`client/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `REACT_APP_API_URL` | No | Backend URL (default: `http://localhost:8000`) |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/llm/providers` | List available LLM providers and models |
| `POST` | `/llm/test` | Test an API key connection |
| `POST` | `/answer/` | Submit a question (with optional LLM config) |

## Supported LLM Models

| Provider | Models |
|----------|--------|
| **Google** | Gemini Pro, Gemini 1.5 Pro, Gemini 2.0 Flash |
| **Anthropic** | Claude Sonnet 4.6, Claude Haiku 4.5, Claude Opus 4.8 |
| **OpenAI** | GPT-4o, GPT-4o Mini, GPT-4.1 |

## Logging

Logs are written to `server/logs/stockbot.log` (rotating, 5MB max, 3 backups) and stdout. Each request logs:

- HTTP method, path, status code, response time
- Question received (provider, model, truncated query)
- Vector search results count
- Answer generation status
- Errors with full stack traces

## License

MIT
