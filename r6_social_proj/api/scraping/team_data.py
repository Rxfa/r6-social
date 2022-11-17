import os
import json
import logging

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://liquipedia.net"
TEAM_DATA_URL = "https://liquipedia.net/rainbowsix/Portal:Teams"
GLOBAL_POINTS_URL = (
    "https://liquipedia.net/rainbowsix/Six_Invitational/2023/Global_Standings"
)

list_of_teams = []
global_standings = []


def main():
    get_global_points(GLOBAL_POINTS_URL)
    get_team_data(TEAM_DATA_URL)


def export_to_json(filename, data):
    """
    Exports given data list to JSON file.
    """
    logger.info("Exporting %s to JSON file.", filename)
    with open(f"../json/{filename}.json", "w+", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False, indent=4))
        logger.info("%s exported to json/%s.json successfully!", data, filename)


def get_global_points(url):
    """
    Makes GET request to url argument, with a 10 timeout.
    Then it extracts teams global points standings and exports to a JSON file.
    """
    logger.info("Scraping global points standings")
    page = requests.get(url, timeout=10)
    soup = BeautifulSoup(page.content, "html.parser")
    for row in soup.select(".table-responsive tbody tr")[1:]:
        team_global_points = {
            "place": row.select_one("td b").text,
            "subregion": row.select_one(".league-icon-small-image a")["title"],
            "team": row.select_one('span[class="team-template-team-standard"]')[
                "data-highlightingclass"
            ],
            "points": row.select("td")[3].select_one("b").text,
            "max points": row.select("td")[4].text,
            "status": get_team_qualification_status(row.select_one("td")),
            "regional league": {
                "1st stage": row.select("td[colspan='1']")[0].text,
                "2nd stage": row.select("td[colspan='1']")[2].text,
                "3rd stage": row.select("td[colspan='1']")[4].text,
            },
            "major": {
                "February": row.select("td[colspan='1']")[1].text,
                "August": row.select("td[colspan='1']")[3].text,
                "November": row.select("td[colspan='1']")[5].text,
            },
        }
        try:
            default_points(team_global_points, "regional league")
            default_points(team_global_points, "major")
        finally:
            global_standings.append(team_global_points)
            logger.info("Global points standings have been scraped successfully")
            export_to_json("global_standings", global_standings)


def default_points(team, competition):
    """
    Changes items value to 0 if it equals 0.
    """
    for key, value in team[competition].items():
        team[competition][key] = 0 if value == "X" else value


def get_team_qualification_status(row):
    """
    Team rows are color coded according to Six Invitation qualification status.
    Returns Team Six Invitational qualification status.
    """
    match row["style"]:
        case "background-color:rgb(221,244,221)":
            status = "Qualified to Six Invitational"
        case "background-color:rgb(251,223,223)":
            status = "Cannot qualify via points"
        case _:
            status = "Can qualify to Six Invitational"
    return status


def get_team_data(url):
    """
    Iterates through every table and makes GET a request
    if a link to a team profile is found.
    """
    page = requests.get(url, timeout=10).text
    soup = BeautifulSoup(page, "lxml")
    for table in soup.find_all("table", class_="wikitable"):
        if table.find("span", class_="team-template-text").find("a")["href"]:
            page = requests.get(
                f"{BASE_URL}{table.find('span', class_='team-template-text').find('a')['href']}",
                timeout=10,
            ).content
            soup = BeautifulSoup(page, "html.parser")
            get_team(soup)
        else:
            continue
    return export_to_json("team_data", list_of_teams)


def get_team(soup):
    """
    Makes GET request to url argument with a 10s timeout.
    Then it gets data on team and appends to list_of_teams.
    """
    name = soup.find("div", class_="infobox-header").text.split("]")[-1]
    folder_name = "_".join(name.lower().split(" "))
    infobox = soup.find_all("div", class_="infobox-cell-2")
    country = infobox[1].text
    region = infobox[3].text.strip()
    team_data = {
        "name": name,
        "country": country.strip(),
        "region": region.strip(),
    }
    list_of_teams.append(team_data)
    team_logos(soup, folder_name)
    return list_of_teams


def team_logos(soup, name):
    """
    Gets team image and saves to media/logos/team/<name arg>
    """
    image_url = f"../../media/logos/teams/{name}/{name}.png"
    if os.path.isfile(image_url):
        logger.info("%s.png has already been saved", name)
    else:
        img_path = soup.find("div", class_="floatnone").find("img")["src"]
        image_data = requests.get(f"{BASE_URL}{img_path}", timeout=10)
        with open(image_url, "wb") as handler:
            handler.write(image_data.content)


if __name__ == "__main__":
    main()
