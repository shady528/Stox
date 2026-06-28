from langchain_google_genai import ChatGoogleGenerativeAI
from app.logger import get_logger

logger = get_logger("stockbot.llm")

PROVIDERS = {
    "google": {
        "name": "Google",
        "models": [
            {"id": "gemini-pro", "name": "Gemini Pro"},
            {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro"},
            {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash"},
        ],
    },
    "anthropic": {
        "name": "Anthropic",
        "models": [
            {"id": "claude-sonnet-4-6", "name": "Claude Sonnet 4.6"},
            {"id": "claude-haiku-4-5", "name": "Claude Haiku 4.5"},
            {"id": "claude-opus-4-8", "name": "Claude Opus 4.8"},
        ],
    },
    "openai": {
        "name": "OpenAI",
        "models": [
            {"id": "gpt-4o", "name": "GPT-4o"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
            {"id": "gpt-4.1", "name": "GPT-4.1"},
        ],
    },
}


def create_llm(provider: str, model_name: str, api_key: str):
    logger.info(f"Creating LLM: provider={provider} model={model_name}")
    if provider == "google":
        return ChatGoogleGenerativeAI(
            model=model_name, google_api_key=api_key, temperature=0.5
        )
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=model_name, anthropic_api_key=api_key, temperature=0.5
        )
    elif provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model_name, openai_api_key=api_key, temperature=0.5
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")


def test_connection(provider: str, model_name: str, api_key: str) -> dict:
    try:
        llm = create_llm(provider, model_name, api_key)
        logger.info(f"Testing connection to {provider}/{model_name}")
        llm.invoke("Say hello in one word.")
        logger.info(f"Connection test passed for {provider}/{model_name}")
        return {"success": True, "message": "Connection successful"}
    except Exception as e:
        logger.error(f"Connection test failed for {provider}/{model_name}: {e}")
        return {"success": False, "message": str(e)}
