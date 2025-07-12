from fastapi import FastAPI
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from routes import base, data
from stores.llm.LLMProviderFactory import LLMProviderFactory


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    settings = get_settings()
    
    # Initialize MongoDB connection
    app.state.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.state.db_client = app.state.mongo_conn[settings.MONGODB_DATABASE]
    print("Connected to MongoDB!")

    # Setup the LLMFactory
    llm_provider_factory = LLMProviderFactory(settings)
    
    # Generation Client
    app.state.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.state.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    print(f"{settings.GENERATION_BACKEND} Generation Model loaded successfully!")

    # Embedding Client
    app.state.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.state.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                                   embedding_size=settings.EMBEDDING_MODEL_SIZE)

    print(f"{settings.EMBEDDING_BACKEND} Embedding Model loaded successfully!")

    yield  # This separates startup from shutdown code
    
    # Shutdown code
    app.state.mongo_conn.close()
    print("Closed MongoDB connection!")

app = FastAPI(lifespan=lifespan)

# Include your routers
app.include_router(base.base_router)
app.include_router(data.data_router)