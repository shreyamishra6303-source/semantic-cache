from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    backend_name:str
    base_url:str
    model:str

    model_config = SettingsConfigDict(env_file=".env",extra="ignore")

settings=Settings()