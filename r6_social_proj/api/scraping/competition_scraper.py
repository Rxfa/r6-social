from enum import Enum, auto
import logging
import json
import requests
from myutils.util import convert_to_json
from bs4 import BeautifulSoup
import competitions

logging.basicConfig(filename="competition_scraper.log", encoding="utf-8", level=logging.DEBUG)
logger = logging.getLogger(__name__)

@convert_to_json
def main(competition, system):
    """Main function"""
    scraped_competition = CompetitionScraper(url=competition, system_of_competition=system)
    logger.info(f"Scraped {scraped_competition.name} successfully!")
    return (
        f"competitions/{'_'.join(scraped_competition.name.split())}",
        scraped_competition.to_json(),
        True
        )

class SystemsOfCompetition(Enum):
    """Systems of competition"""
    CUP_SYSTEM_WITH_PLAYER_PRIZES = auto()
    CUP_SYSTEM_WITH_NO_PLAYER_PRIZES = auto()
    LEAGUE_SYSTEM_WITH_NO_PLAYER_PRIZES = auto()

class CompetitionScraper:
    """
    Extracts data about a given competition.
    """

    def __init__(self, url, system_of_competition):
        self.url = url
        self.name = None
        self.system_of_competition = getattr(SystemsOfCompetition, system_of_competition.upper()).name
        self.participants = None
        self.standings = None
        self.mvp = None
        self.player_stats = None
        self.map_picks = None
        logger.info(f"Starting to scrape {self.url}...")
        self.search()

    def to_json(self):
        """Serialize to JSON"""
        if self.system_of_competition in (SystemsOfCompetition.CUP_SYSTEM_WITH_PLAYER_PRIZES.name, SystemsOfCompetition.LEAGUE_SYSTEM_WITH_NO_PLAYER_PRIZES.name):
            output_file = json.dumps(self, ensure_ascii=False, default=lambda x: x.__dict__, indent=4)
        elif self.system_of_competition == SystemsOfCompetition.CUP_SYSTEM_WITH_NO_PLAYER_PRIZES.name:
            output_file = json.dumps(self, ensure_ascii=False, default=lambda x: x.__dict__, indent=4)
        return output_file

    def search(self):
        """Gets competition page html"""
        page = requests.get(self.url, timeout=10)
        logger.debug(f"Making GET request to {self.url}...")
        soup = BeautifulSoup(page.content, "lxml")
        self.get_competition_overview(soup)
        self.get_competition_participants(soup)
        self.get_player_stats(soup)
        self.get_map_picks(soup)

        if self.system_of_competition == SystemsOfCompetition.CUP_SYSTEM_WITH_PLAYER_PRIZES.name:
            self.get_competition_mvp(soup)
        elif self.system_of_competition == SystemsOfCompetition.LEAGUE_SYSTEM_WITH_NO_PLAYER_PRIZES.name:
            self.get_competition_standings(soup)
        elif self.system_of_competition == SystemsOfCompetition.CUP_SYSTEM_WITH_NO_PLAYER_PRIZES.name:
            pass

    def get_competition_overview(self, page):
        """
        Returns competition name
        """

        def get_name(overview_card):
            return overview_card.select_one("h1[class='pg-title impact__title']").text.strip()

        overview_card = page.select_one("#overview > div > div")
        overview_card.small.extract()

        self.name = get_name(overview_card)

    def get_competition_participants(self, page):
        """
        Returns competition participants.
        """
        participants = page.select(
            "div[id='teams'] div[class^='card card--fade card--link card--has-trunk']"
        )
        def get_team_name(team):
            team.img.extract()
            return team.select_one("a div").text.strip()

        self.participants = [get_team_name(team) for team in participants]

    def get_competition_standings(self, page):
        """Returns competition standings."""
        standings_table_rows = page.select("div[id='stage--1'] table tbody tr")
        def get_team_placement(team_table_row):
            team_table_row.img.extract()
            return dict(
                position=team_table_row.select_one("td:nth-of-type(1)").text,
                team=team_table_row.select_one("td:nth-of-type(2) > a").text,
                points=team_table_row.select_one("td:nth-of-type(3)").text,
                w_ow_ol_l=team_table_row.select_one("td:nth-of-type(4)").text,
                round_difference=team_table_row.select_one("td:nth-of-type(5)").text
            )
        self.standings = [get_team_placement(team_table_row) for team_table_row in standings_table_rows]

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
        Returns every player statistics for competition.
        """
        stats_table = page.select("div[id='playertable'] table tbody tr[role]")
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
        Returns every map defense winrate for competition.
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
    # CUP_SYSTEMS_WITH_PLAYER_PRIZES is a list unlike the others.
    #for e in competitions.CUP_SYSTEMS_WITH_PLAYER_PRIZES:
    #    main(e, "CUP_SYSTEM_WITH_PLAYER_PRIZES")
    for region in competitions.CUP_SYSTEMS_WITH_NO_PLAYER_PRIZES.values():
        for e in region:
            main(e, "CUP_SYSTEM_WITH_NO_PLAYER_PRIZES")
    for region in competitions.LEAGUE_SYSTEMS_WITH_NO_PLAYER_PRIZES.values():
        for e in region:
            main(e, "LEAGUE_SYSTEM_WITH_NO_PLAYER_PRIZES")
