from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


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


class ChallengeType(Enum):
    """Represents a challenge type."""

    NORM = 0
    LAST = 1
    EXT = 2
    TIMEOUT = 3


class Server(Enum):
    """Represents the server region."""

    JP = auto()
    TC = auto()
    SC = auto()
    UNKNOWN = auto()

    def __str__(self):
        if self == Server.JP:
            return "JP"
        if self == Server.TC:
            return "TC"
        if self == Server.SC:
            return "SC"

        return "UNKNOWN"

    @classmethod
    def get_server(cls, name: str) -> Server:
        if name == "JP":
            return Server.JP
        if name == "TC":
            return Server.TC
        if name == "SC":
            return Server.SC
        return Server.UNKNOWN
