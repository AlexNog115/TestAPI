import os 
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

#load variables form .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Load enviroment variables from file or set defaults
    """
    APP_NAME: str = os.getenv("APP_NAME", "User Management API")
    APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")
    APP_ENVIROMENT: str = os.getenv("APP_ENVIROMENT", "development")
    DEBUG: bool = os.getenv("DEBUG","True").lower() == "true"






#global instance for configurations
settings = Settings()

if __name__ == "__main__":
    import pprint
    pprint.pp(dict(settings))