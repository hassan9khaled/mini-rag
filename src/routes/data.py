from fastapi import APIRouter, FastAPI, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignal
import aiofiles 
import logging
from .schemes.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.db_schemes import Data_Chunk


logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix = "/api/v1/data",
    tags = ["api_v1", "data"],
)

@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: str, file: UploadFile,
                      app_settings: Settings = Depends(get_settings)):
    

    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    # Validate file properties
    data_controller = DataController()
    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": result_signal
            }
        )
    
    
    project_dir_path = ProjectController().get_project_path(project_id=project_id)

    file_path, file_id = data_controller.generate_unique_filepath(
        original_file_name=file.filename,
        project_id=project_id)
    try:

        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)

    except Exception as e:

        logger.error(f"Error While uploading file: {e}")

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPOLADED_FAILED.value
            }
        )        

    return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOADED_SUCCESS.value,
                "file_id": file_id,
            }
            )

@data_router.post("/process/{project_id}")
async def process(request: Request, project_id: str, process_request: ProcessRequest):
    
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlab_size = process_request.overlab_size
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )


    process_controller = ProcessController(project_id=project_id)

    file_content = process_controller.get_file_content(file_id=file_id)

    file_chunks = process_controller.process_file_content(
        file_content=file_content,
        file_id=file_id,
    )

    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
                content={
                    "signal": ResponseSignal.PROCESSING_FAILED.value
                }
                )        
    
    

    file_chunks_records = [
        Data_Chunk(
            chunk_text=chunk.page_content,
            chunk_order=i+1,
            chunk_metadata=chunk.metadata,
            chunk_project_id=project.id,
        ) # type: ignore
        for i, chunk in enumerate(file_chunks)
    ]


    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.state.db_client
    )


    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(
            project_id=project.id
        )

    num_records = await chunk_model.insert_many_chunks(chunks=file_chunks_records)
    return JSONResponse(
                content={
                    "signal": ResponseSignal.PROCESSING_SUCCESS.value,
                    "inserted_chunks": num_records
                }
                )   