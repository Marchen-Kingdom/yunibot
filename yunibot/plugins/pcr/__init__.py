import operator
import pathlib
from datetime import datetime, timedelta, timezone
from typing import Tuple

from nonebot import get_driver
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp.event import GroupMessageEvent
from nonebot.adapters.cqhttp.message import MessageSegment
from nonebot.log import logger
from nonebot.plugin import on_command

from .config import Settings
from .data import BOSS_HP, SCORE_RATES
from .db import ClanManager
from .typing import ChallengeType, Server

SERVERS = ["JP", "TC", "SC"]
RANK_GUIDE_TYPES = ["前卫", "中卫", "后卫"]


global_config = get_driver().config
settings = Settings(**global_config.dict())

cache_dir = pathlib.Path(settings.cache_dir).absolute()
db_dir = cache_dir.joinpath("db")
img_dir = cache_dir.joinpath("img")

if not db_dir.exists():
    db_dir.mkdir(parents=True)
if not img_dir.exists():
    img_dir.mkdir(parents=True)

db_name = settings.pcr_db_name
db_path = db_dir.joinpath(db_name)
db_url = f"sqlite:///{str(db_path)}"
clan_manager = ClanManager(db_url)

guide_names = settings.pcr_rank_guide_names.split(",")
if len(guide_names) != 3:
    logger.error(f"Expected 3 rank guide names, but got {len(guide_names)}")


async def _on_bot_connect(bot: Bot):
    await clan_manager.connect()


get_driver().on_bot_connect(_on_bot_connect)

# pylint: disable=invalid-name
create_clan = on_command("建会", block=True)


@create_clan.handle()
async def handle_create_clan(bot: Bot, event: GroupMessageEvent):
    msg = str(event.get_message()).strip().split()
    if len(msg) != 2:
        await create_clan.finish("输入错误")

    group_id = event.group_id
    clan_name, server = msg
    if await clan_manager.clan_exists(group_id):
        await create_clan.finish("公会已存在")
    server = server.upper()
    if server not in SERVERS:
        await create_clan.finish("服务器不合法")

    await clan_manager.create_clan(group_id, clan_name, server)
    await create_clan.finish("成功建立公会")


join_clan = on_command("入会", block=True)


@join_clan.handle()
async def handle_join_clan(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    if not await clan_manager.clan_exists(group_id):
        await join_clan.finish("公会尚未建立")

    user_id = event.user_id
    if await clan_manager.member_exists(group_id, user_id):
        await join_clan.finish("成员已存在")

    msg = str(event.get_message()).strip()
    if msg:
        nickname = msg
    else:
        member_info = await bot.get_group_member_info(
            group_id=group_id, user_id=user_id
        )
        nickname = member_info["nickname"]

    await clan_manager.add_member(group_id, user_id, nickname)
    await join_clan.finish("成功加入公会")


list_members = on_command("查看成员", block=True)


@list_members.handle()
async def handle_list_members(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    if not await clan_manager.clan_exists(group_id):
        await list_members.finish("公会尚未建立")

    nicknames = await clan_manager.list_members(group_id)
    if not nicknames:
        await list_members.finish("公会尚无成员")
    await list_members.finish("\n".join(nicknames))


rank_guides = on_command("指南", block=True)


@rank_guides.handle()
async def handle_rank_guides(bot: Bot, event: GroupMessageEvent):
    msg = str(event.get_message()).strip()
    args = msg.split()
    if len(args) != 1:
        await rank_guides.finish("输入错误")
    guide_type = args[0]
    if guide_type not in RANK_GUIDE_TYPES:
        await rank_guides.finish("输入错误")

    if guide_type == RANK_GUIDE_TYPES[0]:
        rank_guide = guide_names[0]
    elif guide_type == RANK_GUIDE_TYPES[1]:
        rank_guide = guide_names[1]
    else:
        rank_guide = guide_names[2]

    rank_guide_path = f"file:///{img_dir.joinpath(rank_guide)}"
    guide_img = MessageSegment.image(rank_guide_path)
    await rank_guides.finish(guide_img, at_sender=True)


def get_tz(server: Server) -> int:
    if server == Server.JP:
        return 9
    return 8


def get_date(time: datetime, tz: int = 8) -> Tuple[int, int, int]:
    time = time.astimezone(timezone(timedelta(hours=tz - 5)))
    y = time.year
    m = time.month
    d = time.day

    if d < 10:
        m -= 1
    if m < 1:
        m = 12
        y = y - 1

    return (y, m, d)


def next_boss(round_: int, boss: int) -> Tuple[int, int]:
    return (round_, boss + 1) if boss < 5 else (round_ + 1, 1)


def get_stage(round_: int, server: Server) -> int:
    if server == Server.SC:
        return 4 if round_ >= 11 else 3 if round_ >= 6 else 2 if round_ >= 2 else 1

    return (
        5
        if round_ >= 45
        else 4
        if round_ >= 35
        else 3
        if round_ >= 11
        else 2
        if round_ >= 4
        else 1
    )


def get_boss_info(round_: int, boss: int, server: Server) -> Tuple[int, float]:
    stage = get_stage(round_, server)
    boss_hp = BOSS_HP[str(server)][stage - 1][boss - 1]
    score_rate = SCORE_RATES[str(server)][stage - 1][boss - 1]
    return boss_hp, score_rate


async def get_current_progress(
    group_id: int, year: int, month: int, server: Server
) -> Tuple[int, int, int]:
    challenges = await clan_manager.get_challenges(group_id, year, month)
    if len(challenges) == 0:
        round_ = 1
        boss = 1
        remaining_hp, _ = get_boss_info(round_, boss, server)
        return round_, boss, remaining_hp

    challenges.sort(key=operator.attrgetter("time"), reverse=True)
    last_challenge = challenges[0]
    round_ = last_challenge.round_
    boss = last_challenge.boss

    remaining_hp, _ = get_boss_info(round_, boss, server)
    for challenge in challenges:
        if challenge.round_ == round_ and challenge.boss == boss:
            remaining_hp -= challenge.damage
        else:
            break
    if remaining_hp <= 0:
        round_, boss = next_boss(round_, boss)
        remaining_hp, _ = get_boss_info(round_, boss, server)
    return round_, boss, remaining_hp


show_progress = on_command("进度", block=True)


@show_progress.handle()
async def handle_show_progress(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    if not await clan_manager.clan_exists(group_id):
        await show_progress.finish("公会尚未建立")

    now = datetime.now()
    year, month, _ = get_date(now)
    _, _, server_code = await clan_manager.get_clan(group_id)
    server = Server.get_server(server_code)
    round_, boss, remaining_hp = await get_current_progress(
        group_id, year, month, server
    )
    boss_hp, _ = get_boss_info(round_, boss, server)
    stage = get_stage(round_, server)
    report = "目前状态：\n\n"
    report += f"周目：{round_}\n"
    report += f"阶段：{stage}\n"
    report += f"Boss：{1}\n"
    report += f"剩余血量：{remaining_hp}/{boss_hp}"
    await show_progress.finish(report)


add_challenge = on_command("出刀", block=True)


@add_challenge.handle()
async def handle_add_challenge(bot: Bot, event: GroupMessageEvent):
    msg = str(event.get_message()).strip()
    args = msg.split(" ")
    if len(args) == 0:
        await add_challenge.finish("输入不能为空")
    if len(args) != 1 and len(args) != 3:
        await add_challenge.finish("输入错误")
    round_ = None
    boss = None
    damage = None
    if len(args) == 1:
        try:
            damage = int(args[0])
        except ValueError:
            await add_challenge.finish("输入错误")
    if len(args) == 3:
        try:
            round_ = int(args[0])
            boss = int(args[1])
            damage = int(args[2])
        except ValueError:
            await add_challenge.finish("输入错误")

    group_id = event.group_id
    if not await clan_manager.clan_exists(group_id):
        await add_challenge.finish("公会尚未建立")

    user_id = event.user_id
    if not await clan_manager.member_exists(group_id, user_id):
        await add_challenge.finish("成员不存在")

    _, _, server_code = await clan_manager.get_clan(group_id)
    server = Server.get_server(server_code)
    now = datetime.now()
    year, month, _ = get_date(now)
    cur_round, cur_boss, _ = await get_current_progress(group_id, year, month, server)
    round_ = round_ or cur_round
    boss = boss or cur_boss

    type_ = ChallengeType.NORM

    id_ = await clan_manager.add_challenge(
        year, month, group_id, user_id, now, round_, boss, damage, type_  # type: ignore
    )

    report = f"出刀编号E{id_}：\n\n"
    report += f"周目：{round_}\n"
    report += f"Boss：{boss}\n"
    report += f"伤害：{damage}"
    await add_challenge.finish(report, at_sender=True)
