import asyncio
from typing import List

import sqlalchemy
from databases import Database

from .model import clans, members, metadata


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
        row = await self.db.execute(clans.select().where(clans.c.group_id == group_id))
        if row == -1:
            return False
        return True

    async def member_exists(self, group_id: int, user_id: int) -> bool:
        row = await self.db.execute(
            members.select().where(
                members.c.group_id == group_id and members.c.user_id == user_id
            )
        )
        if row == -1:
            return False
        return True

    async def create_clan(self, group_id: int, clan_name: str, server: str):
        # pylint: disable=no-value-for-parameter
        await self.db.execute(
            clans.insert().values(group_id=group_id, clan_name=clan_name, server=server)
        )

    async def add_member(self, group_id: int, user_id: int, nickname: str):
        # pylint: disable=no-value-for-parameter
        await self.db.execute(
            members.insert().values(
                group_id=group_id, user_id=user_id, nickname=nickname
            )
        )

    async def list_members(self, group_id: int) -> List[str]:
        rows = await self.db.fetch_all(
            sqlalchemy.select([members.c.nickname]).where(
                members.c.group_id == group_id
            )
        )
        return [nickname for (nickname,) in rows]
