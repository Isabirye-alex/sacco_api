from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def DATABASE_URL(self) -> str:
        return f"{self.DATABASE_URL}"


settings = Settings()
