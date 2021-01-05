from nonebot import get_driver
from nonebot.adapters import Bot
from nonebot.plugin import on_keyword
from nonebot.rule import to_me

from .config import Config

global_config = get_driver().config
config = Config(**global_config.dict())

hello = on_keyword({"zai?", "在?", "在？", "在吗", "在么？", "在嘛", "在嘛？"}, rule=to_me())


@hello.handle()
async def say_hello(bot: Bot):
    await hello.finish("はい！私はいつも貴方の側にいますよ！")
