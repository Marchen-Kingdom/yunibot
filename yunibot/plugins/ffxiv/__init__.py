import random

from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp.event import GroupMessageEvent
from nonebot.plugin import on_message
from nonebot.typing import T_State


async def is_jumbo_cactpot(bot: Bot, event: Event, state: T_State) -> bool:
    msg = str(event.get_message()).strip()
    return msg == "来点仙人彩"


# pylint: disable=invalid-name
jumbo_cactpot = on_message(rule=is_jumbo_cactpot)


@jumbo_cactpot.handle()
async def handle_jumbo_cactpot(bot: Bot, event: GroupMessageEvent):
    nums = random.sample(range(0, 10), 4)
    await jumbo_cactpot.finish(
        f"仙人彩号码推荐：{''.join([str(num) for num in nums])}", at_sender=True
    )
