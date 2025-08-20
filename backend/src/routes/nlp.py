from fastapi import FastAPI, APIRouter, status, Request
from fastapi.responses import JSONResponse
from routes.schemes.nlp import PushRequest, SearchRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from controllers import NLPController
from controllers import AgentController
from models import ResponseSignal
from models.AssetModel import AssetModel
from controllers import DataController
import os
import logging

logger = logging.getLogger("uvicorn.error")

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1", "nlp"]
)

@nlp_router.post("/index/push/{project_name}")
async def index_project(request: Request, project_name: str, push_request: PushRequest):
    
    # Get or create the project
    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )
    
    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.state.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_name=project_name
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
        generation_client=request.app.state.generation_client,
        template_parser = request.app.state.template_parser
    )
    # Create an asset record in the database
    asset_model = await AssetModel.create_instance(
        db_client=request.app.state.db_client
    )

    asset_record = await asset_model.get_asset_record(asset_project_id=project.id, asset_name=push_request.asset_name)
    asset_id = asset_record.id

    project_has_records = True
    page_num = 1
    inserted_items_count = 0
    idx = 0

    while project_has_records:

        page_chunks = await chunk_model.get_asset_chunks(asset_id=asset_id, page_num=page_num)
        
        
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

@nlp_router.get("/index/info/projects")
async def info_projects(request: Request):
   
    nlp_controller = NLPController(
        vectordb_client=request.app.state.vectordb_client,
        embedding_client=request.app.state.embedding_client,
        generation_client=request.app.state.generation_client,
        template_parser = request.app.state.template_parser
    )

    collection_info = nlp_controller.list_all_projects()

    return JSONResponse(
        content={
            "signal": ResponseSignal.VECTORDB_COLLECTION_RETRIEVED.value,
            "collection_info":collection_info
        }
    )


@nlp_router.get("/index/info/{project_name}")
async def info_project(request: Request, project_name: str):
   
    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )
    project = await project_model.get_project_or_create_one(
        project_name=project_name
    )
    nlp_controller = NLPController(
        vectordb_client=request.app.state.vectordb_client,
        embedding_client=request.app.state.embedding_client,
        generation_client=request.app.state.generation_client,
        template_parser = request.app.state.template_parser
    )

    collection_info = nlp_controller.get_vector_db_collection_info(project=project)

    return JSONResponse(
        content={
            "signal": ResponseSignal.VECTORDB_COLLECTION_RETRIEVED.value,
            "collection_info":collection_info
        }
    )

@nlp_router.post("/index/search/{project_name}")
async def search_index(request: Request, project_name: str, search_request: SearchRequest):

   
    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_name=project_name
    )

    nlp_controller = NLPController(
        vectordb_client=request.app.state.vectordb_client,
        embedding_client=request.app.state.embedding_client,
        generation_client=request.app.state.generation_client,
        template_parser = request.app.state.template_parser
    )

    results = nlp_controller.search_vector_db_collection(
        project=project,
        text=search_request.text,
        limit=search_request.limit,
        assets=search_request.assets
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
            "collection_info":[result.dict() for result in results]
        }
    )

@nlp_router.post("/index/answer/{project_name}")
async def answer_rag(request: Request, project_name: str, search_request: SearchRequest):

   
    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_name=project_name
    )

    nlp_controller = NLPController(
        vectordb_client=request.app.state.vectordb_client,
        embedding_client=request.app.state.embedding_client,
        generation_client=request.app.state.generation_client,
        template_parser = request.app.state.template_parser
    )

    csv_assets = []

    for asset in search_request.assets:
        if ".csv" in asset:
            csv_assets.append(asset)

    search_request.assets = list(set(search_request.assets) - set(csv_assets))

    if len(search_request.assets) == 0:
        agent_controller = AgentController()
        agent_controller.get_session_id()
        response = agent_controller.run(asset = csv_assets, prompt = search_request.text)
        if response:
            agent_response = agent_controller.get_session_info()
            img_path = agent_response.get("img_path")
            if img_path:
                
                img_path = "/imgs/" + img_path
                
            return JSONResponse(
                    content={
                        "signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
                        "answer": agent_response.get("text"),
                        "image_path": img_path
                    }
                )
  
    answer, full_prompt, chat_history = nlp_controller.answer_rag_question(
        project=project,
        query=search_request.text,
        limit=search_request.limit,
        assets=search_request.assets
    )

    if not answer:

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.RAG_ANSWER_ERROR.value,
            }
        )
    

    return JSONResponse(
        content={
            "signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_histroy": chat_history
        }
    )