import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.routes import router
from app.logger import get_logger

logger = get_logger("stockbot.server")

app = FastAPI(title="StockBot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    logger.info(f">>> {request.method} {request.url.path}")
    response = await call_next(request)
    elapsed = round((time.time() - start) * 1000)
    logger.info(f"<<< {request.method} {request.url.path} | {response.status_code} | {elapsed}ms")
    return response


app.include_router(router)

logger.info("StockBot API started")
