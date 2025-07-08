from fastapi import APIRouter, FastAPI, Depends
import os
from helpers.config import get_settings, Settings

base_router = APIRouter(
    prefix = "/api/v1",
    tags = ["api_v1"],
)

@base_router.get("/") # Default route
async def welcome(app_settings: Settings = Depends(get_settings)):

    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION

    return {
        "app_name": app_name,
        "version": app_version
    }