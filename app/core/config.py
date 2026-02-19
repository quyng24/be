from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    SESSION_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str
    ALLOWED_EMAILS: list[str] = [
        "nquy50771@gmail.com",
        "phanthanhnhanh2460@gmail.com",
        "nguyenhuuhoapeace@gmail.com",
    ]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
