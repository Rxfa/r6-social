import logging
import requests
from bs4 import BeautifulSoup
from myutils.util import convert_to_json

logger = logging.getLogger(__name__)

BASE_URL = "https://liquipedia.net"
COMPETITION_URLS = [
    "https://old.siege.gg/competitions/387-six-invitational-2022?tab=results&stats=full-stats",
    "https://liquipedia.net/rainbowsix/Six_Invitational/2022",
]


@convert_to_json
def main():
    page = requests.get(COMPETITION_URLS[0], timeout=10).content
    soup = BeautifulSoup(page, "html.parser")
    competition = dict()
    (
        competition["name"],
        competition["dates"],
        competition["location"],
    ) = get_competition_overview(soup)
    competition["participants"] = get_competition_teams(soup)
    competition["mvp"] = get_competition_mvp(soup)
    competition["player stats"] = get_competition_player_stats(soup)
    competition["map picks"] = get_map_picks(soup)
    return "_".join(competition["name"].split()), competition


def get_competition_overview(raw):
    """
    Returns competition's name, dates(start and end) and location.
    """
    overview_card = raw.select_one("#overview > div > div")
    dates = overview_card.select_one("small > time").text
    overview_card.small.extract()
    name = overview_card.select_one("h1[class='pg-title impact__title']").text.strip()
    location = overview_card.select_one(
        "div[class='card card-body border-0 py-2'] ul > li:nth-child(4) > span:last-child span[class='mr-1']"
    ).text
    return name, dates, location


def get_competition_teams(raw):
    """
    Returns the list of participants of competition referenced in url argument.
    """
    participants = raw.select(
        "div[id='teams'] div[class^='card card--fade card--link card--has-trunk'] "
    )
    def get_team_name(team):
        team.img.extract()
        return team.select_one("a div").text.strip()
    result = [get_team_name(team) for team in participants]
    return result


def get_competition_mvp(raw):
    """
    Returns competition Most Valuable Player.
    """
    logger.info("scraping MVP data.")
    mvp_card = raw.select_one("div[class='nook nook--player nook--stat nook--award award--mvp mb-3 w-100']")
    mvp = dict(
        player=mvp_card.select_one("div:first-child h4 > a").text,
        rating=mvp_card.select_one("div:last-child > div:first-child > div:nth-child(2)").text,
        operators=dict(
            attack=mvp_card.select_one("div[class='col-6 stat__number'] > span:first-child > a > span").text,
            defense=mvp_card.select_one("div[class='col-6 stat__number'] > span:last-child > a > span").text,
        ),
    )
    logger.info("MVP data has been scraped successfully")
    return mvp


def get_competition_player_stats(raw):
    """
    Returns every player statistics
    """
    stats_table = raw.select("div[id='playertable'] table tbody tr")
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
    player_stats = [get_row_stats(player) for player in stats_table]
    return player_stats


def get_map_picks(raw):
    """
    Returns defense winrate for every map.
    """
    map_cards = raw.select("div[class^='card card--map']")
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
    map_picks = [get_map_info(map) for map in map_cards]
    return map_picks


if __name__ == "__main__":
    main()
