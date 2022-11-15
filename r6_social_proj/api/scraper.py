import json
import logging

import requests
from bs4 import BeautifulSoup

PEOPLE_DATA_URL = "https://liquipedia.net/rainbowsix/Portal:Players/All"
GLOBAL_POINTS_URL = "https://liquipedia.net/rainbowsix/Six_Invitational/2023/Global_Standings"

list_of_staff = []
list_of_players = []
global_points_standings = []

def main():
    get_people_data(PEOPLE_DATA_URL)
    get_global_points(GLOBAL_POINTS_URL)



def export_to_json(filename, data):
    """
    Exports given data list to JSON file.
    """
    with open(f"json/{filename}.json", "w+", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False, indent=4))

def get_global_points(url):
    """
    Gets teams global points standings and saves to JSON file.
    """
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    for row in soup.select(".table-responsive tbody tr")[1:]:
        team_global_points = {
            "place":  row.select_one("td b").text,
            "subregion": row.select_one('.league-icon-small-image a')["title"],
            "team": row.select_one('span[class="team-template-team-standard"]')["data-highlightingclass"],
            "points": row.select("td")[3].select_one("b").text,
            "max points": row.select("td")[4].text,
            "status": get_team_qualification_status(row.select_one("td")),
            "regional league": {
                "1st stage": row.select("td[colspan='1']")[0].text,
                "2nd stage": row.select("td[colspan='1']")[2].text,
                "3rd stage": row.select("td[colspan='1']")[4].text,
            },
            "major" : {
                "February": row.select("td[colspan='1']")[1].text,
                "August": row.select("td[colspan='1']")[3].text,
                "November": row.select("td[colspan='1']")[5].text,
            }
        }
        try:
            default_points(team_global_points, "regional league")
            default_points(team_global_points, "major")
        finally:
            global_points_standings.append(team_global_points)
            export_to_json("global_standings", global_points_standings)

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
    Invokes get_staff() or get_players() to get either player or staff data,
    depending on whose data the table of current iteration holds.
    At the end, saves the scraped data to a JSON file.
    """
    page = requests.get(url).text
    soup = BeautifulSoup(page, "html.parser")
    for table in soup.find_all("table", class_="wikitable"):
        # Every table of staff & talents has an 'abbr' tag
        if table.find("abbr"):
            get_staff(table)
        else:
            get_players(table)

    export_to_json("players", list_of_players)
    export_to_json("staff", list_of_staff)

def get_staff(table):
    """
    Gets non-players data, stores in dict and appends to list_of_staff.
    """
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

            list_of_staff.append(staff_info)
    logging.info("Staff data scrapped successfully!")
    return list_of_staff.sort(key=lambda x: x["team"])


def get_players(table):
    """
    Gets players data, stores in dict and appends to list_of_players.
    """
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
            list_of_players.append(player_info)
    logging.info("Player data scrapped successfully!")
    return list_of_players.sort(key=lambda x: x["team"])


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


if __name__ == "__main__":
    main()
