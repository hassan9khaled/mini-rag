from enum import Enum

class LLMEnums(Enum):
    OPENAI = "OPENAI"
    COHERE = "COHERE"
    OLLAMA = "OLLAMA"

class OpenAIEnums(Enum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"