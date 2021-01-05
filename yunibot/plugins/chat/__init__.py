from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp.event import GroupMessageEvent
from nonebot.plugin import on_keyword, on_message
from nonebot.rule import to_me
from nonebot.typing import T_State

# pylint: disable=C0103
hello = on_keyword({"zai?", "在?", "在？", "在吗", "在么？", "在嘛", "在嘛？"}, rule=to_me())


@hello.handle()
async def say_hello(bot: Bot):
    await hello.finish("はい！私はいつも貴方の側にいますよ！")


async def is_waifu(bot: Bot, event: Event, state: T_State) -> bool:
    if not event.is_tome():
        return False

    msg = str(event.get_message()).strip()
    if msg in ["老婆", "老公", "waifu", "laopo"]:
        return True

    return False


waifu = on_message(rule=is_waifu)


@waifu.handle()
async def handle_waifu(bot: Bot, event: Event):
    if event.get_user_id() in bot.config.superusers:
        await bot.send(event, message="mua~", at_sender=True)
    else:
        await bot.send(event, message="你给我滚！", at_sender=True)


async def is_nihaole(bot: Bot, event: Event, state: T_State) -> bool:
    msg = str(event.get_message()).strip()
    return msg == "我好了"


nihaole = on_message(rule=is_nihaole)


@nihaole.handle()
async def handle_nihaole(bot: Bot, event: GroupMessageEvent):
    await bot.set_group_ban(
        self_id=event.self_id,
        group_id=event.group_id,
        user_id=event.user_id,
        duration=60,
    )
    await bot.send(event, "不许好，憋回去！", at_sender=True)
