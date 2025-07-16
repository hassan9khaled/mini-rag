from fastapi import FastAPI, APIRouter, status, Request
from fastapi.responses import JSONResponse
from routes.schemes.nlp import PushRequest, SearchRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from controllers import NLPController
from models import ResponseSignal

import logging

logger = logging.getLogger("uvicorn.error")

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1", "nlp"]
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: str, push_request: PushRequest):
    
    # Get or create the project
    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )
    
    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.state.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR
            }
        )
    
    nlp_controller = NLPController(
        vectordb_client=request.app.state.vectordb_client,
        embedding_client=request.app.state.embedding_client,
        generation_client=request.app.state.generation_client
    )

    project_has_records = True
    page_num = 1
    inserted_items_count = 0
    idx = 0

    while project_has_records:

        page_chunks = await chunk_model.get_project_chunks(project_id=project.id, page_num=page_num)
        print(page_chunks)
        
        if len(page_chunks):
            page_num += 1
        
        if not page_chunks or len(page_chunks) == 0:
            
            project_has_records = False
            break

        chunks_ids = list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)

        is_inserted = nlp_controller.index_into_vector_db(
            project=project,
            chunks=page_chunks,
            do_reset=push_request.do_reset,
            chunks_ids=chunks_ids
        )
        

        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.INSERT_INTO_VECTORDB_ERROR
                }
            )
        
        inserted_items_count += len(page_chunks)


    return JSONResponse(
        content={
            "signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
            "inserted_items_count": inserted_items_count
        }
    )

@nlp_router.get("/index/info/{project_id}")
async def index_project(request: Request, project_id: str):
   
    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )
    nlp_controller = NLPController(
        vectordb_client=request.app.state.vectordb_client,
        embedding_client=request.app.state.embedding_client,
        generation_client=request.app.state.generation_client
    )

    collection_info = nlp_controller.get_vector_db_collection_info(project=project)

    return JSONResponse(
        content={
            "signal": ResponseSignal.VECTORDB_COLLECTION_RETRIEVED.value,
            "collection_info":collection_info
        }
    )

@nlp_router.post("/index/search/{project_id}")
async def index_project(request: Request, project_id: str, search_request: SearchRequest):

   
    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    nlp_controller = NLPController(
        vectordb_client=request.app.state.vectordb_client,
        embedding_client=request.app.state.embedding_client,
        generation_client=request.app.state.generation_client
    )

    results = nlp_controller.search_vector_db_collection(
        project=project,
        text=search_request.text,
        limit=search_request.limit
    )
    
    if not results:
        
        return JSONResponse(
            content={
                "signal": ResponseSignal.VECTORDB_SEARCH_ERROR.value
            }
        )


    return JSONResponse(
        content={
            "signal": ResponseSignal.VECTORDB_SEARCH_SUCCESS.value,
            "collection_info":results
        }
    )
