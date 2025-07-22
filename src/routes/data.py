from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignal
import aiofiles 
import logging
from .schemes.data import ProcessRequest, ProjectRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.db_schemes import Data_Chunk, Asset
from models.enums.AssetModelEnum import AssetModelEnum
from datetime import datetime, timezone

# Logger setup
logger = logging.getLogger('uvicorn.error')

# API router for data-related endpoints
data_router = APIRouter(
    prefix = "/api/v1/data",
    tags = ["api_v1", "data"],
)



@data_router.post("/project/create/{project_name}")
async def create_project(request: Request, project_name: str):

    # Get or create the project
    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_name=project_name
    )

    if project:
        return JSONResponse(
            content={
                "signal": ResponseSignal.PROCESS_SUCCESS.value
            }
        )

@data_router.post("/upload/{project_name}")
async def upload_data(request: Request, project_name: str, file: UploadFile,
                       app_settings: Settings = Depends(get_settings)):
    """
    Uploads a file to a specific project.

    This endpoint handles file validation, storage, and database recording.

    Args:
        request (Request): The incoming request object.
        project_name (str): The ID of the project to upload the file to.
        file (UploadFile): The file to be uploaded.
        app_settings (Settings, optional): Application settings. 
                                           Defaults to Depends(get_settings).

    Returns:
        JSONResponse: A response indicating the result of the upload.
    """
    
    # Get or create the project
    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_name=project_name
    )

    # Validate the uploaded file
    data_controller = DataController()
    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": result_signal}
        )
    
    # Generate a unique file path
    file_path, file_id = data_controller.generate_unique_filepath(
        original_file_name=file.filename,
        project_name=project_name
    )

    # Save the file to the server
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
                
    except Exception as e:
        logger.error(f"Error while uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.FILE_UPOLADED_FAILED.value}
        )

    # Create an asset record in the database
    asset_model = await AssetModel.create_instance(
        db_client=request.app.state.db_client
    )
    asset_resource = Asset(
        asset_project_name=project.id,
        asset_type=AssetModelEnum.FILE.value,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path),
        created_at=datetime.now(timezone.utc)
    ) # type: ignore
    asset_record = await asset_model.create_asset(asset=asset_resource)

    return JSONResponse(
        content={
            "signal": ResponseSignal.FILE_UPLOADED_SUCCESS.value,
            "asset_id": str(asset_record.id),
            "file_id_name": file_id,
        }
    )

@data_router.post("/process/{project_name}")
async def process(request: Request, project_name: str, process_request: ProcessRequest):
    """
    Processes files in a project, creating text chunks.

    This endpoint reads files, splits them into chunks, and stores them in the database.

    Args:
        request (Request): The incoming request object.
        project_name (str): The ID of the project to process.
        process_request (ProcessRequest): The processing parameters.

    Returns:
        JSONResponse: A response indicating the result of the processing.
    """
    
    # Extract processing parameters
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    # Get or create the project
    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )
    project = await project_model.get_project_or_create_one(
        project_name=project_name
    )

    # Get the files to process
    asset_model = await AssetModel.create_instance(
        db_client=request.app.state.db_client
    )
    project_files_ids = {}
    if process_request.file_id:
        asset_record = await asset_model.get_asset_record(
            asset_project_name=project.id,
            asset_name=process_request.file_id
        )
        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseSignal.FILE_ID_ERROR.value}
            )
        project_files_ids = {asset_record.id: asset_record.asset_name}
    else:
        project_files = await asset_model.get_all_project_assets(
            asset_project_name=project.id,
            asset_type=AssetModelEnum.FILE.value,
        )
        project_files_ids = {record.id: record.asset_name for record in project_files}

    if not project_files_ids:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.NO_FILES_ERROR.value}
        )

    # Process the files
    process_controller = ProcessController(project_name=project_name)
    num_records = 0
    num_files = 0
    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.state.db_client
    )

    if do_reset == 1:
        await chunk_model.delete_chunks_by_project_name(project_id=project.id)

    for asset_id, file_id in project_files_ids.items():
        file_content = process_controller.get_file_content(file_id=file_id)
        if file_content is None:
            logger.error(f"Error while processing file: {file_id}")
            continue

        file_chunks, records_signal = process_controller.process_file_content(
            file_content=file_content,
            file_id=file_id,
            chunk_size=chunk_size,
            overlap_size=overlap_size
        )
        if not file_chunks:
            return JSONResponse(
                content={"signal": ResponseSignal.PROCESSING_FAILED.value}
            )

        file_chunks_records = [
            Data_Chunk(
                chunk_text=chunk.page_content,
                chunk_order=i + 1,
                chunk_metadata=chunk.metadata,
                chunk_project_id=project.id,
                chunk_asset_id=asset_id
            ) # type: ignore
            for i, chunk in enumerate(file_chunks)
        ]

        num_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
        num_files += 1

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value if not records_signal else ResponseSignal.RECORDS_EXCEEDED.value,
            "inserted_chunks": num_records,
            "processed_files": num_files
        }
    )

@data_router.get("/projects/info")
async def list_all_projects(request: Request):
    # Get or create the project
    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )

    projects, pages = await project_model.get_all_projects()

    if not projects:

        return JSONResponse(
            content={
                "signal": ResponseSignal.NO_PROJECTS_FOUND.value,
                "projects": []
            }
        )

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESS_SUCCESS.value,
            "projects": projects,
            "pages": pages
        }
    )

@data_router.delete("/projects/delete")
async def delete_project(request: Request, project_request: ProjectRequest):
    
    # Get or create the project
    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )
    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.state.db_client
    )

    project = await project_model.get_project(
        project_name=project_request.project_name
    )    

    asset_model = await AssetModel.create_instance(
        db_client=request.app.state.db_client
    )

    if project:

        request.app.state.vectordb_client.delete_collection(f"collection_{project_request.project_name}")

        await asset_model.delete_assets_by_project_name(project.id)
        await chunk_model.delete_chunks_by_project_name(project.id)

        _ = ProjectController().delete_project(project_name=project_request.project_name)
        await project_model.delete_project(project_name=project_request.project_name)


        return JSONResponse(
            content={
                "signal": f"{project_request.project_name} project deleted successfully"
            }
        )
        
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
        }
    )

@data_router.get("/projects/rename")
async def list_all_projects(request: Request, project_request: ProjectRequest):
    # Get or create the project
    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )

    