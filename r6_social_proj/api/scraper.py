"""
Small script to scrape information(Nationality, nickname, real name and team) on known r6 pro players
"""

import requests
from bs4 import BeautifulSoup

URL = "https://liquipedia.net/rainbowsix/Portal:Players/All"
page = requests.get(URL).text
soup = BeautifulSoup(page, "lxml")

list_of_players = []
list_of_staff = []

def main():
    for table in soup.find_all("table", class_="wikitable"):
        # Every table of staff & talents has an 'abbr' tag
        if table.find("abbr"):
            get_staff(table)
        else:
            get_players(table)

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
            }
            list_of_players.append(player_info)
    return list_of_players


if __name__ == "__main__":
    main()