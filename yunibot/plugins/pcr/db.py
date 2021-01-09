import asyncio
from dataclasses import dataclass
from typing import List, Tuple

import sqlalchemy
from databases import Database

from .model import challenge, clan, member, metadata


@dataclass
class Challenge:
    """Represents a challenge."""

    id_: int
    year: int
    month: int
    group_id: int
    user_id: int
    time: int
    round_: int
    boss: int
    damage: int
    type_: int


class ClanManager:
    """Clan manager.

    Clan manager is an interface used by the PCR plugin to perform database operations,
    such as adding a new clan.
    """

    def __init__(self, url: str):
        self.url = url
        self.db = Database(self.url)

    async def connect(self):
        engine = sqlalchemy.create_engine(self.url)
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, metadata.create_all, engine)
        await self.db.connect()

    async def clan_exists(self, group_id: int) -> bool:
        row = await self.get_clan(group_id)
        if row is None:
            return False
        return True

    async def member_exists(self, group_id: int, user_id: int) -> bool:
        query = member.select().where(
            member.c.group_id == group_id and member.c.user_id == user_id
        )
        row = await self.db.fetch_one(query=query)
        if row is None:
            return False
        return True

    async def create_clan(self, group_id: int, clan_name: str, server: str):
        # pylint: disable=no-value-for-parameter
        await self.db.execute(
            clan.insert().values(group_id=group_id, clan_name=clan_name, server=server)
        )

    async def get_clan(self, group_id: int) -> Tuple[int, str, str]:
        query = clan.select().where(clan.c.group_id == group_id)
        return await self.db.fetch_one(query=query)

    async def add_member(self, group_id: int, user_id: int, nickname: str):
        # pylint: disable=no-value-for-parameter
        await self.db.execute(
            member.insert().values(
                group_id=group_id, user_id=user_id, nickname=nickname
            )
        )

    async def list_members(self, group_id: int) -> List[str]:
        rows = await self.db.fetch_all(
            sqlalchemy.select([member.c.nickname]).where(member.c.group_id == group_id)
        )
        return [nickname for (nickname,) in rows]

    async def add_challenge(
        self,
        group_id: int,
        user_id: int,
        time: int,
        round_: int,
        boss: int,
        damage: int,
        type_: int,
    ):
        # pylint: disable=no-value-for-parameter
        query = challenge.insert()
        values = {
            "group_id": group_id,
            "user_id": user_id,
            "time": time,
            "round": round_,
            "boss": boss,
            "damage": damage,
            "type": type_,
        }
        await self.db.execute(query=query, values=values)

    async def get_challenges(
        self, group_id: int, year: int, month: int
    ) -> List[Challenge]:
        query = challenge.select().where(
            challenge.c.group_id == group_id
            and challenge.c.year == year
            and challenge.c.month == month
        )
        rows = await self.db.fetch_all(query=query)
        return [
            Challenge(
                id_, year, month, group_id, user_id, time, round_, boss, damage, type_
            )
            for (
                id_,
                year,
                month,
                group_id,
                user_id,
                time,
                round_,
                boss,
                damage,
                type_,
            ) in rows
        ]
