import os
import json
import logging

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

TEAM_DATA_URL = "https://liquipedia.net/rainbowsix/Portal:Teams"
PEOPLE_DATA_URL = "https://liquipedia.net/rainbowsix/Portal:Players/All"
GLOBAL_POINTS_URL = (
    "https://liquipedia.net/rainbowsix/Six_Invitational/2023/Global_Standings"
)
BIRTHDAY_LIST_URL = "https://liquipedia.net/rainbowsix/Birthday_list"

BASE_URL = "https://liquipedia.net"


list_of_teams = []
staff_list = []
player_list = []
birthday_list = []
global_standings = []


def main():
    get_global_points(GLOBAL_POINTS_URL)
    get_people_data(PEOPLE_DATA_URL)
    get_birthdays(BIRTHDAY_LIST_URL)
    get_team_data(TEAM_DATA_URL)


def export_to_json(filename, data):
    """
    Exports given data list to JSON file.
    """
    logger.info("Exporting %s to JSON file.", filename)
    with open(f"json/{filename}.json", "w+", encoding="utf-8") as file:
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


def get_people_data(url):
    """
    Makes GET request to url argument, with a 10s timeout.
    Then it invokes get_staff() or get_players() to get either player or staff data,
    depending on whose data the table of current iteration holds.
    At the end, exports the scraped data to a JSON file.
    """
    logger.info("Scraping players and staff data")
    page = requests.get(url, timeout=10)
    soup = BeautifulSoup(page.content, "html.parser")
    for table in soup.find_all("table", class_="wikitable"):
        # Every table of staff & talents has an 'abbr' tag
        if table.find("abbr"):
            get_staff(table)
        else:
            get_players(table)
    logger.info("Players and staff data have been scraped successfully")
    export_to_json("player_list", player_list)
    export_to_json("staff_list", staff_list)


def get_staff(table):
    """
    Gets non-players data, stores in dict and appends to staff_list.
    """
    logger.info("Scraping staff data")
    for row in table.find_all("tr"):
        if row.find("th"):
            continue
        else:
            country = row.find("img")["alt"]
            id = row.find_all("a")[1].text
            real_name = row.find_all("td")[1].text if row.find_all("td")[1] else ""
            role = row.find_all("td")[2].text if row.find_all("td")[2] else ""
            team = (
                row.find("span", class_="team-template-text").find("a").text
                if row.find("span", class_="team-template-text")
                else ""
            )
            staff_info = {
                "country": country.strip(),
                "nickname": id.strip(),
                "real name": real_name.strip(),
                "team": team.strip(),
                "role": role.split()[-1].strip(""),
                "status": get_status(row)
                if len(row.find("td")["style"].split(":")) == 3
                else "active",
            }

            staff_list.append(staff_info)
    logging.info("Staff data scraped successfully!")
    return staff_list.sort(key=lambda x: x["team"])


def get_players(table):
    """
    Gets players data, stores in dict and appends to player_list.
    """
    logger.info("Scraping players data")
    for row in table.find_all("tr"):
        if row.find("th"):
            continue
        else:
            country = row.find("img")["alt"]
            id = row.find_all("a")[1].text
            team = (
                row.find("span", class_="team-template-text").find("a").text
                if row.find("span", class_="team-template-text")
                else "LFT"
            )
            real_name = row.find_all("td")[1].text if row.find_all("td")[1] else ""
            player_info = {
                "country": country,
                "nickname": id.strip(),
                "real name": real_name.strip(),
                "team": team.strip(),
                "role": "Player",
                "status": get_status(row)
                if len(row.find("td")["style"].split(":")) == 3
                else "active",
            }
            player_list.append(player_info)
    logging.info("Players data scrapped successfully!")
    return player_list.sort(key=lambda x: x["team"])


def get_status(row):
    """
    Player/Staff rows are color coded according to status.
    Returns person status.
    """
    match (row.find("td")["style"].split(":")[2]):
        case "#d3d8f8":
            status = "inactive"
        case "#e5e5e5":
            status = "retired"
        case _:
            status = "active"
    return status


def get_birthdays(url):
    """
    Makes GET request to url argument with a 10s timeout.
    Then it gets every player and community personalities birthdays and exports to JSON file.
    """
    logger.info("Scraping birthday list")
    page = requests.get(url, timeout=10)
    soup = BeautifulSoup(page.content, "html.parser")
    for row in soup.select("table tbody tr")[1:]:
        row.span.extract()
        player = {
            "nickname": row.select_one("td > a").text,
            "name": row.select("td")[-1].text,
            "day of month": row.select("td")[1].text,
            "year": row.select("td")[0].text,
        }
        birthday_list.append(player)
    logger.info("Birthday list scraped successfully")
    birthday_list.sort(key=lambda x: x["year"])
    export_to_json("birthday_list", birthday_list)


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
    image_url = f"../media/logos/teams/{name}/{name}.png"
    if os.path.isfile(image_url):
        logger.info("%s.png has already been saved", name)
    else:
        img_path = soup.find("div", class_="floatnone").find("img")["src"]
        image_data = requests.get(f"{BASE_URL}{img_path}", timeout=10)
        with open(image_url, 'wb') as handler:
            handler.write(image_data.content)

if __name__ == "__main__":
    main()
