from pydantic import BaseSettings


class Settings(BaseSettings):
    cache_dir: str
    pcr_db_name: str
    pcr_rank_guide_names: str

    class Config:
        extra = "ignore"
