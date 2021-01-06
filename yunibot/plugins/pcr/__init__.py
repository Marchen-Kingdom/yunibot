import pathlib

import sqlalchemy
from databases import Database
from nonebot import get_driver
from nonebot.adapters import Bot

from .config import Settings

global_config = get_driver().config
settings = Settings(**global_config.dict())

cache_dir = pathlib.Path(settings.cache_dir).absolute()
db_dir = cache_dir.joinpath("db")

if not db_dir.exists():
    db_dir.mkdir(parents=True)

db_name = settings.pcr_db_name
db_path = db_dir.joinpath(db_name)
db_url = f"sqlite:///{str(db_path)}"

database = Database(db_url)
engine = sqlalchemy.create_engine(db_url)

metadata = sqlalchemy.MetaData()
clans = sqlalchemy.Table(
    "clans",
    metadata,
    sqlalchemy.Column("group_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("clan_name", sqlalchemy.String),
    sqlalchemy.Column("server", sqlalchemy.String),
)


async def _on_bot_connect(bot: Bot):
    metadata.create_all(engine)
    await database.connect()


get_driver().on_bot_connect(_on_bot_connect)
