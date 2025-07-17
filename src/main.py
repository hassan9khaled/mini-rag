from fastapi import FastAPI
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from routes import base, data, nlp
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    settings = get_settings()
    
    # Initialize MongoDB connection
    app.state.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.state.db_client = app.state.mongo_conn[settings.MONGODB_DATABASE]
    print("\x1b[36mConnected to MongoDB!\033[0m")

    # Setup the LLMFactory
    llm_provider_factory = LLMProviderFactory(settings)
    
    # Generation Client
    app.state.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.state.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    print(f"\x1b[36m{settings.GENERATION_BACKEND} Generation Model loaded successfully!\033[0m")

    # Embedding Client
    app.state.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.state.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                                   embedding_size=settings.EMBEDDING_MODEL_SIZE)

    print(f"\x1b[36m{settings.EMBEDDING_BACKEND} Embedding Model loaded successfully!\033[0m")

    # Setup the VectorDBFactory
    vectordb_provider_factory = VectorDBProviderFactory(settings)

    # VectorDB Client
    app.state.vectordb_client = vectordb_provider_factory.create(
        provider=settings.VECTOR_DB_BACKEND
    )

    app.state.vectordb_client.connect()
    print(f"\x1b[36mConnected to {settings.VECTOR_DB_BACKEND.capitalize()}DB!\033[0m")

    app.state.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG
    )
    
    yield  # This separates startup from shutdown code
    
    # Shutdown code
    app.state.mongo_conn.close()
    print("\x1b[33mClosed MongoDB connection!\033[0m")

    app.state.vectordb_client.disconnect()
    print(f"\x1b[33mClosed {settings.VECTOR_DB_BACKEND.capitalize()}DB connection!\033[0m")

app = FastAPI(lifespan=lifespan)

# Include your routers
app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)