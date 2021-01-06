from pydantic import BaseSettings


class Settings(BaseSettings):
    cache_dir: str

    class Config:
        extra = "ignore"
