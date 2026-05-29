from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://vibe:vibepass@localhost:5432/vibecoding"
    secret_key: str = "change-this-secret-key-in-production"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    mail_server: str = "smtp.gmail.com"
    mail_port: int = 587
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    class Config:
        env_file = ".env"


settings = Settings()
