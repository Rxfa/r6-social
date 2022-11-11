"""
Small script to scrape information(Nationality, nickname, real name and team) on known r6 pro players
"""

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://liquipedia.net"

list_of_teams = []
list_of_players = []
list_of_staff = []


def main():
    people_data_url = "https://liquipedia.net/rainbowsix/Portal:Players/All"
    team_data_url = "https://liquipedia.net/rainbowsix/Portal:Teams"
    get_people_data(people_data_url)
    get_team_data(team_data_url)
    print(list_of_staff, end="\n\n")
    print(f"there are {len(list_of_staff)} entries.", end="\n\n")


def get_team_data(url):
    page = requests.get(url).text
    soup = BeautifulSoup(page, "lxml")
    for table in soup.find_all("table", class_="wikitable"):
        if table.find("span", class_="team-template-text").find("a")["href"]:
            page = requests.get(
                f"{BASE_URL}{table.find('span', class_='team-template-text').find('a')['href']}"
            ).text
            soup = BeautifulSoup(page, "lxml")
        else:
            continue
    return list_of_teams


def get_people_data(url):
    page = requests.get(url).text
    soup = BeautifulSoup(page, "lxml")
    for table in soup.find_all("table", class_="wikitable"):
        # Every table of staff & talents has an 'abbr' tag
        if table.find("abbr"):
            get_staff(table)
        else:
            #            get_players(table)
            continue


def get_staff(table):
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
                "role": role.strip(),
                "status": get_status(row) if len(row.find("td")["style"].split(":")) == 3 else "active",
            }
            list_of_staff.append(staff_info)
    return list_of_staff


def get_players(table):
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
                "status": get_status(row) if len(row.find("td")["style"].split(":")) == 3 else "active",
            }
            list_of_players.append(player_info)
    return list_of_players


def get_status(row):
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
