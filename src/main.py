from fastapi import FastAPI
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from routes import base, data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    settings = get_settings()
    
    # Initialize MongoDB connection
    app.state.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.state.db_client = app.state.mongo_conn[settings.MONGODB_DATABASE]
    print("Connected to MongoDB!")
    
    yield  # This separates startup from shutdown code
    
    # Shutdown code
    app.state.mongo_conn.close()
    print("Closed MongoDB connection!")

app = FastAPI(lifespan=lifespan)

# Include your routers
app.include_router(base.base_router)
app.include_router(data.data_router)