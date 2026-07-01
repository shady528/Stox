import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Embedding: "google" (cloud) | "local" (instructor-large)
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "google")

# Vector store: "pinecone" (cloud) | "chroma" (local)
VECTOR_STORE = os.getenv("VECTOR_STORE", "pinecone")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "stockbot")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "/app/data/chroma")

# Ollama (offline mode)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# Default LLM: "google" (online) | "ollama" (offline)
DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "google")

if VECTOR_STORE == "pinecone" and not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY is required when VECTOR_STORE=pinecone")
