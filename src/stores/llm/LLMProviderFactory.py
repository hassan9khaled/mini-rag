from .LLMEnums import LLMEnums
from .providers import CoHereProvider, OpenAIProvider

class LLMProviderFactory:
    def __init__(self, config: dict):
        self.config = config

    def create(self, provider: str):
        if provider == LLMEnums.OPENAI.value or provider == LLMEnums.OLLAMA.name:
            return OpenAIProvider(
                api_key=self.config.OPENAI_API_KEY,
                base_url=self.config.OPENAI_API_URL,
                default_generation_max_output_tokens=self.config.GENERATION_DAFAULT_MAX_TOKENS,
                default_generation_temprature=self.config.GENERATION_DAFAULT_TEMPERATURE,
                default_input_max_charcters=self.config.INPUT_DAFAULT_MAX_CHARACTERS
            )
        
        if provider == LLMEnums.COHERE.value:

            return OpenAIProvider(
                api_key=self.config.COHERE_API_KEY,
                default_generation_max_output_tokens=self.config.GENERATION_DAFAULT_MAX_TOKENS,
                default_generation_temprature=self.config.GENERATION_DAFAULT_TEMPERATURE,
                default_input_max_charcters=self.config.INPUT_DAFAULT_MAX_CHARACTERS
            )
        
        return None