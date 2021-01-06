from pydantic import BaseSettings


class Settings(BaseSettings):
    cache_dir: str
    pcr_db_name: str

    class Config:
        extra = "ignore"
