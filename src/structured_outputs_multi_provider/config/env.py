from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    ollama_url: str
    ollama_model: str

    gemini_url: str
    gemini_model: str
    gemini_api_key: str
    gemini_input_cache_hit_cost: float
    gemini_input_cache_miss_cost: float
    gemini_output_cost: float

    deepseek_url: str
    deepseek_model: str
    deepseek_api_key: str
    deepseek_input_cache_hit_cost: float
    deepseek_input_cache_miss_cost: float
    deepseek_output_cost: float


settings = Settings()
