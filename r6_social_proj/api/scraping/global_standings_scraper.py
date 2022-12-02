import logging
import json
import requests
from bs4 import BeautifulSoup
from myutils.util import convert_to_json

logger = logging.getLogger(__name__)

GLOBAL_POINTS_URL = (
    "https://liquipedia.net/rainbowsix/Six_Invitational/2023/Global_Standings"
)


@convert_to_json
def main():
    """Main function"""
    global_standings = GlobalStandingScraper(GLOBAL_POINTS_URL)
    return "Global_standings", global_standings.to_json(), True


class GlobalStandingScraper:
    """
    Scrapes global standings
    """

    def __init__(self, url):
        self.url = url
        self.standings = None

        self.search()

    def search(self):
        """Gets target page html"""
        page = requests.get(self.url, timeout=10)
        soup = BeautifulSoup(page.content, "lxml")
        self.get_global_standings(soup)

    def to_json(self):
        """Serialize to JSON"""
        return json.dumps(self, ensure_ascii=False, default=lambda x: x.__dict__, indent=4)

    def get_global_standings(self, page):
        """
        Scrapes global standings table
        """
        logger.info("Scraping global points standings")
        global_standings_table = page.select(".table-responsive tbody tr")[1:]
        global_standings = []
        for row in global_standings_table:
            team_global_points = dict(
                place=row.select_one("td b").text,
                subregion=row.select_one(".league-icon-small-image a")["title"],
                team=row.select_one('span[class="team-template-team-standard"]')[
                    "data-highlightingclass"
                ],
                points=row.select("td")[3].select_one("b").text,
                max_points=row.select("td")[4].text,
                status=self.get_team_qualification_status(row.find_all("td")[2]),
                league=dict(
                    stage_1=row.select("td[colspan='1']")[0].text,
                    stage_2=row.select("td[colspan='1']")[2].text,
                    stage_3=row.select("td[colspan='1']")[4].text,
                ),
                major=dict(
                    february=row.select("td[colspan='1']")[1].text,
                    august=row.select("td[colspan='1']")[3].text,
                    november=row.select("td[colspan='1']")[5].text,
                ),
            )
            try:
                self.default_points(team_global_points, "league")
                self.default_points(team_global_points, "major")
            finally:
                global_standings.append(team_global_points)
                logger.info("Global points standings have been scraped successfully")
        self.standings = global_standings

    def get_team_qualification_status(self, row):
        """
        Sets team Six Invitational qualification status according to how it's row is color coded.
        """
        if row.get("style") is None:
            status = "Can qualify to Six Invitational"
        else:
            match row["style"]:
                case "background-color:rgb(221,244,221)":
                    status = "Qualified to Six Invitational"
                case "background-color:rgb(251,223,223)":
                    status = "Cannot qualify via points"
                case _:
                    status = "Can qualify to Six Invitational"
        return status

    def default_points(self, team, competition):
        """
        Changes items value to 0 if it equals 0.
        """
        for key, value in team[competition].items():
            team[competition][key] = 0 if value == "X" else value


if __name__ == "__main__":
    main()
