import os
import logging
import json
import requests
from bs4 import BeautifulSoup
from myutils.util import convert_to_json

logger = logging.getLogger(__name__)

BASE_URL = "https://liquipedia.net"
TEAM_DATA_URL = "https://liquipedia.net/rainbowsix/Portal:Teams"

@convert_to_json
def main():
    """Main function"""
    teams = TeamScraper(TEAM_DATA_URL)
    return "Teams", teams.to_json(), True

class TeamScraper:
    """
    Scrapes information about teams.
    """

    def __init__(self, url):
        self.url = url
        self.teams = []
        self.search()

    def search(self):
        """Gets target page html"""
        page = requests.get(self.url, timeout=10)
        soup = BeautifulSoup(page.content, "lxml")
        self.get_teams(soup)

    def to_json(self):
        """Serialize to JSON"""
        return json.dumps(
            self, ensure_ascii=False, default=lambda x: x.__dict__, indent=4
        )

    def get_teams(self, page):
        """
        Iterates through every table and makes GET a request
        if a link to a team profile is found.
        """
        for table in page.find_all("table", class_="wikitable"):
            if table.find("span", class_="team-template-text").find("a")["href"]:
                team_href = table.find("span", class_="team-template-text").find("a")[
                    "href"
                ]
                req = requests.get(f"{BASE_URL}{team_href}", timeout=10)
                soup = BeautifulSoup(req.content, "lxml")
                self.get_team(soup)
            else:
                continue

    def get_team(self, page):
        """
        Scrapes information for a team
        """
        name = page.find("div", class_="infobox-header").text.split("]")[-1]
        country = page.find_all("div", class_="infobox-cell-2")[1].text
        region = page.find_all("div", class_="infobox-cell-2")[3].text.strip()
        self.teams.append(dict(name=name, country=country.strip(), region=region))
        team_img_filename = "_".join(name.lower().split(" "))
        self.save_team_logo(page, team_img_filename)

    def save_team_logo(self, page, filename):
        """
        Downloads and saves team logo
        """
        image_url = f"../../media/logos/teams/{filename}/{filename}.png"
        if os.path.isfile(image_url):
            logger.info("%s.png has already been saved", filename)
        else:
            img_path = page.find("div", class_="floatnone").find("img")["src"]
            image_data = requests.get(f"{BASE_URL}{img_path}", timeout=10)
            with open(image_url, "wb") as handler:
                handler.write(image_data.content)

if __name__ == "__main__":
    main()
