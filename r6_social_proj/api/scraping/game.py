from dataclasses import dataclass

@dataclass
class Game:
    """
    For scraping game results and stats
    """
    date: str
    competition: str
    played_maps: tuple
    teams: tuple
    result: tuple
    player_stats: list
    operator_bans: tuple
