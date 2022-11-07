"""
Small script to scrape information(Nationality, nickname, real name and team) on known r6 pro players
"""

import requests
from bs4 import BeautifulSoup

URL = "https://liquipedia.net/rainbowsix/Portal:Players/All"
page = requests.get(URL).text
soup = BeautifulSoup(page, "lxml")

tab = soup.find("table", class_="wikitable")

list_of_players = []

for element in soup.find_all("table", class_="wikitable"):
    if element.find("abbr"):
        continue
    else:
        for row in element.find_all("tr"):
            if row.find("th"):
                continue
            else:
                id = row.find_all("a")[1].text

                if row.find("span", class_="team-template-text"):
                    team = row.find("span", class_="team-template-text").find("a").text
                else:
                    team = "LFT"

                if row.find_all("td")[1]:
                    real_name = row.find_all("td")[1].text
                else:
                    real_name = ""

                player_info = {
                    'nickname': id,
                    'real name': real_name.strip(),
                    'team': team if team else 'LFT',
                }
                list_of_players.append(player_info)

#print(list_of_players)
print(len(list_of_players))