import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    # Database Settings
    postgres_user: str = "unibike"
    postgres_password: str = "unibike_password"
    postgres_db: str = "unibike_db"
    postgres_host: str = "localhost"  # Default to localhost for outside-docker testing
    postgres_port: int = 5432

    # Gradio Settings
    gradio_admin_username: str = "admin"
    gradio_admin_password: SecretStr = SecretStr("password")

    # Paths
    chroma_db_dir: str = "./data/chroma"
    data_dir: str = "./data"
    # Groq API
    groq_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @property
    def database_url(self) -> str:
        # Pydantic 2.x way of constructing DSN or just use a standard format
        if self.postgres_host == "localhost":
            return f"sqlite:///{os.path.join(self.data_dir, 'unibike.db')}"
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


settings = Settings()
