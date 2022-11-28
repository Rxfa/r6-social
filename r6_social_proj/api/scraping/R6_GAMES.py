import logging
import json

import requests
from bs4 import BeautifulSoup

GAME_URL="https://siege.gg/matches"


logging.basicConfig()
logger = logging.getLogger(__name__)

games_list=[]

def main():
    get_game_data(GAME_URL)
    

def get_game_data(url):
    logger.info("Scraping future games data")
    page = requests.get(url,timeout=10)
    soup = BeautifulSoup(page.content,"html.parser")
    for table in soup.find_all("div",class_="active"):
            get_games(table)
    logger.info("Game data scraped")
    export_to_json("game_data",games_list)


def get_games(table):
    logger.info("Scraping games")
    for row in table.find_all("a",class_="match"):  #Bug 
             country = row.find("img",class_="flag")["alt"]
             hour = row.find("span",class_="meta__item meta__time").text
             date = row.find("span",class_="meta__item meta__day").text
             team = row.find("span", class_="match__name text-truncate").text
             tournmanet = row.find("span",class_="meta__item meta__competition").text  
    game_info ={
            "team": team,
            "country":country,
            "date":date,
            "hour": hour,
            "tournament":tournmanet
            }
    games_list.append(game_info)
    logger.info("Scraped successfully")
    return games_list


def export_to_json(filename, data):
    """
    Exports given data list to JSON file.
    """
    logger.info("Exporting %s to JSON file.", filename)
    with open(f"json/{filename}.json", "w+", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False, indent=4))
        logger.info("%s exported to json/%s.json successfully!", data, filename)

if __name__ == "__main__":
    main()