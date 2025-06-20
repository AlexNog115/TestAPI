import os 
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pydantic import ConfigDict


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

    # DB configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://usuario:contraseña@localhost:5432/app_db")
    
    # Security configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "clave_secreta_predeterminada")
    ALGORITHM: str = os.getenv("ALGORITHM", "RS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_HOURS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_HOURS", "24"))

    #RSA Keys configuration for JWT signing
    RSA_PRIVATE_KEY_PATH: str = os.getenv("RSA_PRIVATE_KEYS_PATH")
    RSA_PUBLIC_KEY_PATH: str = os.getenv("RSA_PUBLIC_KEY_PATH")
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Ignora variables no definidas en la clase
    )





#global instance for configurations
settings = Settings()

if __name__ == "__main__":
    import pprint
    pprint.pp(dict(settings))