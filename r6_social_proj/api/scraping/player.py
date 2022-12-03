from dataclasses import dataclass
from enum import auto, Enum


class Role(Enum):
    """List of roles"""

    PLAYER = auto()
    COACH = auto()
    ANALYST = auto()
    OBSERVER = auto()
    CASTER = auto()

class Status(Enum):
    """List of statuses"""
    ACTIVE = auto()
    INACTIVE = auto()
    RETIRED = auto()

@dataclass
class Player:
    """Player class"""

    country: str
    nickname: str
    name: str
    team: str
    status: str


@dataclass
class Staff:
    """Staff class"""

    country: str
    nickname: str
    name: str
    team: str
    role: Role
    status: str
