from enum import Enum

class ResponseSignal(Enum):

    FILE_VALIEDATED_SUCCESS = 'file_validate_successfully'
    FILE_TYPE_NOT_SUPPORTED = "file_type_not_supported"
    FILE_SIZE_EXCEEDED = "file_size_exceeded"
    FILE_UPLOADED_SUCCESS = "file_uploaded_success"
    FILE_UPOLADED_FAILED = "file_uploaded_failed"
    PROCESSING_SUCCESS = "processing_success"
    PROCESSING_FAILED = "processing_failed"
    