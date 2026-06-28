from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.rag import get_answer
from app.services.llm_provider import PROVIDERS, test_connection
from app.logger import get_logger

logger = get_logger("stockbot.routes")

router = APIRouter()


class QuestionRequest(BaseModel):
    question: str
    provider: Optional[str] = None
    model_name: Optional[str] = None
    api_key: Optional[str] = None


class AnswerResponse(BaseModel):
    answer: str


class LLMTestRequest(BaseModel):
    provider: str
    model_name: str
    api_key: str


@router.get("/health")
async def health_check():
    return {"status": "healthy"}


@router.get("/llm/providers")
async def get_providers():
    return {"providers": PROVIDERS}


@router.post("/llm/test")
async def test_llm(request: LLMTestRequest):
    logger.info(f"Testing connection: provider={request.provider} model={request.model_name}")
    result = test_connection(request.provider, request.model_name, request.api_key)
    if not result["success"]:
        logger.warning(f"Connection test failed: {result['message']}")
        raise HTTPException(status_code=400, detail=result["message"])
    logger.info("Connection test passed")
    return result


@router.post("/answer/", response_model=AnswerResponse)
async def post_answer(request: QuestionRequest):
    provider_label = request.provider or "default"
    model_label = request.model_name or "gemini-pro"
    logger.info(f"Question received: provider={provider_label} model={model_label} q=\"{request.question[:80]}\"")
    try:
        answer = get_answer(
            request.question,
            provider=request.provider,
            model_name=request.model_name,
            api_key=request.api_key,
        )
        logger.info(f"Answer generated: {len(answer)} chars")
        return AnswerResponse(answer=answer)
    except Exception as e:
        logger.error(f"Error generating answer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
