from contextlib import asynccontextmanager
import logging

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from .api.router import router
from .services.gemini_client import log_gemini_startup_status
from .services.simulator import simulator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Intelligent Care Assistant backend")
    log_gemini_startup_status()
    await simulator.start()
    logger.info("IoT simulator started")
    try:
        yield
    finally:
        logger.info("Stopping Intelligent Care Assistant backend")
        await simulator.stop()
        logger.info("IoT simulator stopped")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
