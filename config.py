from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # env vars names and types
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        # reference the file containing private information for local development
        env_file = ".env"

settings = Settings() #type: ignore