import json
import logging

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

PEOPLE_DATA_URL = "https://liquipedia.net/rainbowsix/Portal:Players/All"
BIRTHDAY_LIST_URL = "https://liquipedia.net/rainbowsix/Birthday_list"
BASE_URL = "https://liquipedia.net"

player_list = []
staff_list = []
birthday_list = []

def main():
    get_birthdays(BIRTHDAY_LIST_URL)
    get_people_data(PEOPLE_DATA_URL)


def export_to_json(filename, data):
    """
    Exports given data list to JSON file.
    """
    logger.info("Exporting %s to JSON file.", filename)
    with open(f"../json/{filename}.json", "w+", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False, indent=4))
        logger.info("%s exported to json/%s.json successfully!", data, filename)


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

if __name__ == "__main__":
    main()
    