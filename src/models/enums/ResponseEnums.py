from enum import Enum

class ResponseSignal(Enum):

    FILE_VALIEDATED_SUCCESS = 'file_validate_successfully'
    FILE_TYPE_NOT_SUPPORTED = "file_type_not_supported"
    FILE_SIZE_EXCEEDED = "file_size_exceeded"
    FILE_UPLOADED_SUCCESS = "file_uploaded_success"
    FILE_UPOLADED_FAILED = "file_uploaded_failed"
    PROCESSING_SUCCESS = "processing_success"
    PROCESSING_FAILED = "processing_failed"
    NO_FILES_ERROR = "files_not_found"
    FILE_ID_ERROR = "no_file_found_with_this_id"
    CHUNKS_RETRIEVED_SUCCESS = "chunks_retrieved_successfully"
    CHUNKS_RETRIEVED_FAILED = "chunks_retrieved_failed"
    PROJECT_NOT_FOUND_ERROR = "project_not_found"
    INSERT_INTO_VECTORDB_ERROR = "insert_into_vectordb_error"
    INSERT_INTO_VECTORDB_SUCCESS = "insert_into_vectordb_success"
    VECTORDB_COLLECTION_RETRIEVED = "vectordb_collection_retrieved"
    VECTORDB_SEARCH_ERROR = "vectordb_search_error"
    VECTORDB_SEARCH_SUCCESS = "vectordb_search_success"
    RAG_ANSWER_ERROR = "rag_answer_error"
    RAG_ANSWER_SUCCESS = "rag_answer_success"    
    PROCESS_SUCCESS = "process_success"
    PROCESS_FAILED = "process_failed"
    NO_PROJECTS_FOUND = "no_projects_found"
    RECORDS_EXCEEDED = "you_csv_file_exceed_the_records_limit"
    