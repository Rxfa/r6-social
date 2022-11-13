import requests
import logging
import json
from bs4 import BeautifulSoup
from os.path import exists

list_of_staff = []
list_of_players = []

def main():
    people_data_url = "https://liquipedia.net/rainbowsix/Portal:Players/All"
    get_people_data(people_data_url)


def get_people_data(url):
    page = requests.get(url).text
    soup = BeautifulSoup(page, "lxml")
    for table in soup.find_all("table", class_="wikitable"):
        # Every table of staff & talents has an 'abbr' tag
        if table.find("abbr"):
            get_staff(table)
        else:
            get_players(table)
        
    with open("json/players.json", "w+") as players:
        players.write(json.dumps(list_of_players, ensure_ascii=False, indent=4))
        
    with open("json/staff.json", "w+") as staff:
        staff.write(json.dumps(list_of_staff, ensure_ascii=False, indent=4))


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
                "role": role.split()[-1].strip(""),
                "status": get_status(row) if len(row.find("td")["style"].split(":")) == 3 else "active",
            }
            list_of_staff.append(staff_info)
    logging.info("Staff data scrapped successfully!")
    return list_of_staff.sort(key=lambda x: x["team"])


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
    logging.info("Player data scrapped successfully!")
    return list_of_players.sort(key=lambda x: x["team"])


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
