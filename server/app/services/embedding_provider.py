from app.config import EMBEDDING_PROVIDER, GOOGLE_API_KEY
from app.logger import get_logger

logger = get_logger("stockbot.embeddings")

PROVIDERS = {
    "google": {
        "name": "Google",
        "model": "models/gemini-embedding-001",
        "dimensions": 3072,
        "description": "Cloud-based, no local RAM required",
    },
    "local": {
        "name": "Local (Instructor-Large)",
        "model": "hkunlp/instructor-large",
        "dimensions": 768,
        "description": "Runs locally, no API key needed, ~2GB RAM — requires separate 768-dim index",
    },
}


def get_embeddings(provider: str = None, api_key: str = None):
    provider = provider or EMBEDDING_PROVIDER

    if provider == "local":
        logger.info("Loading local embedding model: hkunlp/instructor-large")
        from langchain_community.embeddings import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name="hkunlp/instructor-large")
        logger.info("Local embedding model loaded")
        return embeddings

    # default: google
    key = api_key or GOOGLE_API_KEY
    if not key:
        raise ValueError("GOOGLE_API_KEY is required for Google embeddings")
    logger.info("Using Google cloud embeddings: gemini-embedding-001")
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=key,
    )
