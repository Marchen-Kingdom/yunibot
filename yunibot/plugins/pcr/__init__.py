import pathlib

import sqlalchemy
from databases import Database
from nonebot import get_driver
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp.event import GroupMessageEvent
from nonebot.plugin import on_command

from .config import Settings

SERVERS = ["JP", "TC", "SC"]

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

create_clan = on_command("建会")


@create_clan.handle()
async def handle_create_clan(bot: Bot, event: GroupMessageEvent):
    msg = str(event.get_message()).strip().split()
    if len(msg) != 2:
        await create_clan.reject("输入错误")

    group_id = event.group_id
    clan_name, server = msg
    row = await database.fetch_one(clans.select().where(clans.c.group_id == group_id))
    if row:
        await create_clan.reject("公会已存在")
    server = server.upper()
    if server not in SERVERS:
        await create_clan.reject("服务器不合法")
    await database.execute(
        clans.insert().values(group_id=group_id, clan_name=clan_name, server=server)
    )
    await create_clan.finish("成功建立公会")
