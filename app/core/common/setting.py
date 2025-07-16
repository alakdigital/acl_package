from dotenv import load_dotenv
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    
    
    class Config:
        env_file = ".env.local"
        env_file_encoding = "utf-8"
    
    

def reload_settings():
    load_dotenv(override=True)
    return Settings()