import pathlib

from nonebot import get_driver

from .config import Settings

global_config = get_driver().config
settings = Settings(**global_config.dict())

cwd = pathlib.Path.cwd()
cache_dir = cwd.joinpath("db")

if not cache_dir.exists():
    cache_dir.mkdir(parents=True)
