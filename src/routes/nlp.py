from fastapi import FastAPI, APIRouter, status, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger("uvicorn.error")

nlp_router = APIRouter(
    prefix="api/v1/nlp",
    tags=["api/v1", "nlp"]
)