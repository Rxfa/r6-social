from collections import namedtuple
import logging
import json
import requests
from bs4 import BeautifulSoup
from myutils.util import convert_to_json

logger = logging.getLogger(__name__)

COMPETITION_URLS = [
    "https://old.siege.gg/matches?tab=results&competitions%5B%5D=387&page=1",
]

GAME = ["https://old.siege.gg/matches/7220-invitational-intl-team-empire-vs-tsm"]

@convert_to_json
def main():
    """Main function"""
    game = GameScraper(GAME[0])
    return (
        f"games/{'_'.join(game.competition.split())}-{game.teams.team1}_{game.teams.team2}",
        game.to_json(),
        False
    )


class GameScraper:
    """
    For scraping game results and stats
    """

    def __init__(self, url):
        self.url = url
        self.teams = None
        self.rosters = None
        self.score = None
        self.date = None
        self.competition = None
        self.player_stats = None
        self.operator_bans = None
        self.game_results = None

        self.search()

    def to_json(self):
        """Serialize to JSON"""
        return json.dumps(self, default=lambda x: x.__dict__, indent=4)

    def search(self):
        """Returns target url html"""
        search_result = requests.get(self.url, timeout=10)
        soup = BeautifulSoup(search_result.content, "lxml")
        self.parse_overview(soup)
        self.parse_scores(soup)
        self.parse_rosters(soup)
        self.parse_operator_bans(soup)
        self.parse_stats(soup)

    def parse_overview(self, page):
        """Gets match overview data"""
        Teams = namedtuple("Teams", "team1 team2")
        Score = namedtuple("Score", "score1 score2")
        self.teams = Teams(
            page.select_one('.team--a span[class^="match__name"]').text.strip(),
            page.select_one(".team--b span[class^='match__name']").text.strip(),
        )
        self.score = Score(
            page.select_one(".team--a div[class^='match__score']").text,
            page.select_one(".team--b div[class^='match__score']").text,
        )
        self.date = page.select_one("time[class^='meta__item']").text
        self.competition = page.select_one(".meta__competition > a").text

    def parse_scores(self, page):
        """Gets scores for each map"""
        map_list = []
        match_logs = page.select("ol[class^='match__games'] li")
        for map in match_logs:
            map_played = (
                map.select_one("span[class='game__text__won']")
                .text.split("won")[-1]
                .strip()
            )
            team1 = map.select_one("div[class='game__score__item mr-1'] img")["alt"]
            score1 = map.select("span[class='game__score__item']")[0].text
            team2 = map.select_one("div[class='game__score__item ml-1'] img")["alt"]
            score2 = map.select("span[class='game__score__item']")[1].text
            map = dict(name=map_played, result=f"{team1} {score1}-{score2} {team2}")
            map_list.append(map)
        self.game_results = map_list

    def parse_operator_bans(self, page):
        """Gets operator bans for the whole match"""
        played_maps = page.find_all("ol", class_="ban__ops__list list-group list-group-flush")

        def parse_op_bans_by_map(map):
            """Returns operator bans for each map"""
            map_bans = []
            ban_by_team = map.find_all("li")
            for ban in ban_by_team:
                result = {}
                result["team"] = ban.select_one("span[class^='ban__op__team']").text
                result["operator"] = ban.select_one("strong[class^='ban__op__name']").text
                map_bans.append(result)
            return map_bans

        self.operator_bans = [parse_op_bans_by_map(val) for val in played_maps]

    def parse_rosters(self, page):
        """Gets rosters"""
        rosters = page.select("div", class_="roster roster--row")

        def parse_team_roster(team):
            player_profile = team.find_all(
                "li", class_="player__username list-group-item"
            )
            return [i.select_one("h5")["title"] for i in player_profile]

        rosters_list = list(
            filter(
                lambda x: len(x) == 5, [parse_team_roster(roster) for roster in rosters]
            )
        )
        team1, *_, team2 = rosters_list  # to get rid of all duplicates
        self.rosters = {}
        self.rosters[self.teams.team1], self.rosters[self.teams.team2] = team1, team2

    def parse_stats(self, page):
        """Gets player stats for both teams"""
        stats_table = page.find("table", class_="table--player-stats").select("tr")
        self.player_stats = dict()
        self.player_stats[self.teams.team1] = self.parse_team_stats(stats_table[2:7])
        self.player_stats[self.teams.team2] = self.parse_team_stats(stats_table[8:13])

    def parse_team_stats(self, team):
        """Gets player stats for each team"""

        def player_stats(row):
            """Gets each player stats"""
            player_stats = dict(
                name=row.select_one("td", class_="sp__player")["data-sort"],
                rating=row.select_one("td[class^='sp__rating']").text,
                kd=row.select_one("td[class^='sp__kills']").text,
                entry=row.select_one("td[class^='sp__ok']").text,
                kost=row.select_one("td[class^='sp__kost']").text,
                kpr=row.select_one("td[class^='sp__kpr']").text,
                srv=row.select_one("td[class^='sp__srv']").text,
                clutches=row.select_one("td[class^='sp__1vx']").text,
                plants=row.select_one("td[class^='sp__plant']").text,
                hs_percent=row.select_one("td[class^='sp__hs']").text,
                attack=row.select_one("td[class^='sp__atk']")["data-sort"],
                defense=row.select_one("td[class^='sp__def']")["data-sort"],
            )
            return player_stats
        return [player_stats(val) for val in team]


if __name__ == "__main__":
    main()
