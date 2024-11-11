import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import SecretStr


load_dotenv()

class Settings(BaseSettings):
    supabase_url: str =os.getenv('SUPABASE_URL')
    supabase_key: SecretStr = SecretStr(os.getenv('SUPABASE_KEY'))
    db_url: str = os.getenv('DATABASE_URL')
    open_api_key: SecretStr = SecretStr(os.getenv('OPEN_API_KEY'))

    class config:
        env_file = ".env"


settings = Settings()


DATABASE_URL = settings.db_url