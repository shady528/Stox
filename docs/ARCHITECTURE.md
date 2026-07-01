# StockBot Architecture

## Two Versions

StockBot ships in two configurations driven entirely by environment variables.
The codebase is shared; only the Docker build and `.env` differ.

---

## Online Version (Deploy Target)

Everything runs in the cloud. No local models, no GPU required.

| Layer | Technology | Notes |
|---|---|---|
| LLM (default) | Google Gemini 2.5 Flash | Via `GOOGLE_API_KEY` |
| LLM (user override) | Anthropic / OpenAI | Via LLM switcher UI |
| Embeddings | `gemini-embedding-001` | 3072 dims, cloud API |
| Vector store | Pinecone (serverless) | Index dim: 3072 |
| Backend RAM | ~300 MB | No local model |

**Required env vars:**
```
EMBEDDING_PROVIDER=google
VECTOR_STORE=pinecone
GOOGLE_API_KEY=...
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=stockbot
```

---

## Offline Version (Local / Air-gapped)

Everything runs locally. No API keys needed after initial model download.

| Layer | Technology | Notes |
|---|---|---|
| LLM | Ollama — Llama 3 | Runs via Docker sidecar |
| Embeddings | `hkunlp/instructor-large` | 768 dims, local HuggingFace |
| Vector store | Chroma | Persisted to `./data/chroma` on disk |
| Backend RAM | ~3 GB | Embedding model + Ollama |
| GPU | Optional | Ollama uses GPU if available, CPU fallback |

**Required env vars:**
```
EMBEDDING_PROVIDER=local
VECTOR_STORE=chroma
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama3
```

---

## Shared Codebase — Factory Pattern

All switching happens through three factory modules. `rag.py` calls them;
nothing else in the app needs to know which provider is active.

```
server/app/services/
├── embedding_provider.py   # "google" → GoogleGenerativeAIEmbeddings
│                           # "local"  → HuggingFaceEmbeddings (instructor-large)
│
├── vector_store.py         # "pinecone" → PineconeVectorStore  [TO BUILD]
│                           # "chroma"   → ChromaVectorStore    [TO BUILD]
│
├── llm_provider.py         # "google"    → ChatGoogleGenerativeAI
│                           # "anthropic" → ChatAnthropic
│                           # "openai"    → ChatOpenAI
│                           # "ollama"    → ChatOllama           [TO BUILD]
│
└── rag.py                  # calls all three factories, runs the chain
```

---

## File Structure

```
StockBot/
├── server/
│   ├── app/
│   │   ├── services/
│   │   │   ├── embedding_provider.py   ← done
│   │   │   ├── vector_store.py         ← to build
│   │   │   ├── llm_provider.py         ← done (needs ollama added)
│   │   │   ├── rag.py                  ← update to use vector_store factory
│   │   │   └── memory.py               ← done
│   │   ├── config.py                   ← add VECTOR_STORE, OLLAMA_* vars
│   │   ├── routes.py                   ← done
│   │   ├── main.py                     ← done
│   │   └── logger.py                   ← done
│   │
│   ├── requirements.txt                ← shared base (fastapi, uvicorn, langchain core)
│   ├── requirements.online.txt         ← langchain-google-genai, pinecone, langchain-pinecone
│   ├── requirements.offline.txt        ← sentence-transformers, chromadb, langchain-ollama
│   │
│   ├── Dockerfile.online               ← python:3.12-slim + requirements.online.txt
│   ├── Dockerfile.offline              ← python:3.12-slim + requirements.offline.txt
│   │
│   ├── scripts/
│   │   └── upload.py                   ← reads EMBEDDING_PROVIDER + VECTOR_STORE, picks right store
│   └── data/
│       ├── pdfs/                       ← source documents
│       └── chroma/                     ← offline vector store (gitignored)
│
├── client/
│   ├── Dockerfile                      ← same for both versions
│   └── ...
│
├── docker-compose.yml                  ← online: server + client
├── docker-compose.offline.yml          ← offline: server + client + ollama
└── docs/
    └── ARCHITECTURE.md                 ← this file
```

---

## Docker Compose — Online (`docker-compose.yml`)

```yaml
services:
  server:
    build:
      context: ./server
      dockerfile: Dockerfile.online
    env_file: ./server/.env
    ports: ["8000:8000"]
    volumes: ["./server/data:/app/data"]

  client:
    build:
      context: ./client
      args:
        REACT_APP_API_URL: https://<your-railway-url>
    ports: ["3000:80"]
    depends_on: [server]
```

---

## Docker Compose — Offline (`docker-compose.offline.yml`)

```yaml
services:
  ollama:
    image: ollama/ollama
    ports: ["11434:11434"]
    volumes: ["ollama_data:/root/.ollama"]
    # run `docker exec <id> ollama pull llama3` once after first start

  server:
    build:
      context: ./server
      dockerfile: Dockerfile.offline
    environment:
      EMBEDDING_PROVIDER: local
      VECTOR_STORE: chroma
      OLLAMA_HOST: http://ollama:11434
      OLLAMA_MODEL: llama3
    ports: ["8000:8000"]
    volumes:
      - "./server/data:/app/data"   # chroma DB persists here
    depends_on: [ollama]

  client:
    build:
      context: ./client
      args:
        REACT_APP_API_URL: http://localhost:8000
    ports: ["3000:80"]
    depends_on: [server]

volumes:
  ollama_data:
```

---

## What Still Needs to Be Built

| Task | File | Status |
|---|---|---|
| Vector store factory | `server/app/services/vector_store.py` | TODO |
| Add Ollama to LLM provider | `server/app/services/llm_provider.py` | TODO |
| Split requirements | `requirements.txt / .online / .offline` | TODO |
| Online Dockerfile | `server/Dockerfile.online` | TODO |
| Offline Dockerfile | `server/Dockerfile.offline` | TODO |
| Offline docker-compose | `docker-compose.offline.yml` | TODO |
| Update config.py | Add `VECTOR_STORE`, `OLLAMA_*` vars | TODO |
| Update rag.py | Use `vector_store.py` factory | TODO |
| Update upload.py | Use `vector_store.py` factory | TODO |

---

## Deployment Plan (Online Version)

1. Push repo to `github.com/shady528/Stox`
2. Deploy backend → Railway (connect repo, set env vars, auto-builds `Dockerfile.online`)
3. Deploy frontend → Vercel (connect repo, set `REACT_APP_API_URL` to Railway URL)
4. Set `CORS_ORIGINS` on Railway to include the Vercel domain
5. Run `upload.py` once (either locally or via Railway one-off job) to ingest PDFs
