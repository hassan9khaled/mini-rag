from enum import Enum

class LLMEnums(Enum):
    OPENAI = "OPENAI"
    COHERE = "COHERE"
    OLLAMA = "OLLAMA"

class OpenAIEnums(Enum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"

class CoHereEnums(Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "CHATBOT"

    DOCUMENT = 'search_document'
    QUERY = 'search_query'

class DocumentTypeEnum(Enum):
    DOCUMENT = 'document'
    QUERY = 'query'
