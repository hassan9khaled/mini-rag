from fastapi import APIRouter, FastAPI, Depends
import os
from helpers.config import get_settings, Settings

# Create an API router for the base endpoints
base_router = APIRouter(
    prefix = "/api/v1",
    tags = ["api_v1"],
)

@base_router.get("/") # Default route
async def welcome(app_settings: Settings = Depends(get_settings)):
    """
    Default welcome route for the API.

    This endpoint provides basic information about the application,
    including its name and version.

    Args:
        app_settings (Settings, optional): Application settings. 
                                           Defaults to Depends(get_settings).

    Returns:
        dict: A dictionary containing the application name and version.
    """

    # Retrieve app name and version from settings
    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION

    # Return the information as a JSON response
    return {
        "app_name": app_name,
        "version": app_version
    }
