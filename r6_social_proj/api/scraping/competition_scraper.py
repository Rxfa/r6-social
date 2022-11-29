import logging
import json
import requests
from bs4 import BeautifulSoup
from myutils.util import convert_to_json

logger = logging.getLogger(__name__)

BASE_URL = "https://liquipedia.net"
COMPETITION_URLS = [
    "https://old.siege.gg/competitions/342-six-mexico-major-2021?tab=results&stats=full-stats",
    "https://old.siege.gg/competitions/365-six-sweden-major-2021?tab=results&stats=full-stats",
    "https://old.siege.gg/competitions/404-six-charlotte-major-2022?tab=results&stats=full-stats",
    "https://old.siege.gg/competitions/418-six-berlin-major-2022?tab=results&stats=full-stats",
    "https://old.siege.gg/competitions/297-six-invitational-2021?tab=results&stats=full-stats",
    "https://old.siege.gg/competitions/387-six-invitational-2022?tab=results&stats=full-stats",
]


@convert_to_json
def main():
    """Main function"""
    competition = CompetitionScraper(COMPETITION_URLS[0])
    return (
        f"competitions/{'_'.join(competition.name.split())}",
        competition.to_json(),
        True
        )


class CompetitionScraper:
    """
    Scrapes important information for each competition
    """

    def __init__(self, url):
        self.url = url
        self.name = None
        self.dates = None
        self.location = None
        self.participants = None
        self.mvp = None
        self.player_stats = None
        self.map_picks = None

        self.search()

    def to_json(self):
        """Serialize to JSON"""
        return json.dumps(self, ensure_ascii=False, default=lambda x: x.__dict__, indent=4)

    def search(self):
        """Gets target page html"""
        page = requests.get(self.url, timeout=10)
        soup = BeautifulSoup(page.content, "lxml")
        self.get_competition_overview(soup)
        self.get_competition_participants(soup)
        self.get_competition_mvp(soup)
        self.get_player_stats(soup)
        self.get_map_picks(soup)

    def get_competition_overview(self, page):
        """
        Returns competition's name, dates(start and end) and location.
        """
        overview_card = page.select_one("#overview > div > div")
        dates = overview_card.select_one("small > time").text
        overview_card.small.extract()
        name = overview_card.select_one("h1[class='pg-title impact__title']").text.strip()
        location = overview_card.select_one(
            "div[class='card card-body border-0 py-2'] ul > li:nth-child(4) > span:last-child span[class='mr-1']"
        ).text

        self.name = name
        self.dates = dates
        self.location = location

    def get_competition_participants(self, page):
        """
        Returns the list of participants of competition referenced in url argument.
        """
        participants = page.select(
            "div[id='teams'] div[class^='card card--fade card--link card--has-trunk']"
        )
        def get_team_name(team):
            team.img.extract()
            return team.select_one("a div").text.strip()

        self.participants = [get_team_name(team) for team in participants]

    def get_competition_mvp(self, page):
        """
        Returns competition Most Valuable Player.
        """
        logger.info("scraping MVP data.")
        mvp_card = page.select_one("div[class='nook nook--player nook--stat nook--award award--mvp mb-3 w-100']")
        if mvp_card:
            mvp = dict(
                player=mvp_card.select_one("div:first-child h4 > a").text,
                rating=mvp_card.select_one("div:last-child > div:first-child > div:nth-child(2)").text,
                operators=dict(
                    attack=mvp_card.select_one("div[class='col-6 stat__number'] > span:first-child > a > span").text,
                    defense=mvp_card.select_one("div[class='col-6 stat__number'] > span:last-child > a > span").text,
                ),
            )
            logger.info("MVP data has been scraped successfully")
            self.mvp = mvp

    def get_player_stats(self, page):
        """
        Returns every player statistics
        """
        stats_table = page.select("div[id='playertable'] table tbody tr")
        def get_row_stats(row):
            """
            Returns player stats in given row
            """
            player = dict(
                team=row.select_one("td[class^='sp__player'] > a")["title"],
                player=row.select_one("td[class^='sp__player']")["data-sort"],
                rating=row.select_one("td[class^='sp__rating']").text,
                kd=row.select_one("td[class^='sp__kills']").text,
                entry=row.select_one("td[class^='sp__ok']").text,
                maps_played=row.select_one("td[class^='sp__rounds']").text,
                kost=row.select_one("td[class^='sp__kost']").text,
                kpr=row.select_one("td[class^='sp__kpr']").text,
                srv=row.select_one("td[class^='sp__srv']").text,
                clutches=row.select_one("td[class^='sp__1vx']").text,
                plants=row.select_one("td[class^='sp__plant']").text,
                disables=row.select_one("td[class^='sp__disable']").text,
                hs_ratio=row.select_one("td[class^='sp__hs']").text,
                operators=dict(
                    attack=row.select_one("td[class^='sp__atk']")["data-sort"],
                    defense=row.select_one("td[class^='sp__def']")["data-sort"],
                ),
            )
            return player
        self.player_stats = [get_row_stats(player) for player in stats_table]

    def get_map_picks(self, page):
        """
        Returns defense winrate for every map.
        """
        map_cards = page.select("div[class^='card card--map']")
        def get_map_info(map):
            name = map["title"]
            plays, *_ = map.select_one("div:first-child div strong").text.split()
            def_winrate = map.select("div:nth-child(2) ul li div[class^='progress-content']")
            def get_winrates(bombsites):
                return dict(
                    site=bombsites.text.split()[1],
                    winrate=bombsites.select_one("strong").text,
                    rounds=bombsites.select_one("span").text
                )
            return dict(
                name=name,
                plays=plays,
                bombsites=[get_winrates(bombsite) for bombsite in def_winrate]
            )
        self.map_picks = [get_map_info(map) for map in map_cards]

if __name__ == "__main__":
    main()
