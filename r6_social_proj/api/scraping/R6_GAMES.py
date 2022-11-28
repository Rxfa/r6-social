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
    page = requests.get(url, timeout=10)
    soup = BeautifulSoup(page.content, "html.parser")
    upcoming_games = soup.select("div[id^='tab-upcoming'] a")
    game_list = [get_game(game) for game in upcoming_games]
    logger.info("Game data scraped")
    export_to_json("game_data", [get_game(game) for game in upcoming_games])


def get_game(game):
    """Returns upcoming game information"""
    logger.info("Scraping games")
    return dict(
        date=game.select_one("span[class='meta__item meta__day']").text,
        time=game.select_one("span[class='meta__item meta__time']").text,
        competition=game.select_one("span[class='meta__item meta__competition']").text,
        team1=game.select_one("div[class='match__table match__table--b match__table--']:nth-of-type(2) div span[class^='match__name']").text,
        team2=game.select_one("div[class='match__table match__table--b match__table--']:nth-of-type(4) div span[class^='match__name']").text
    )


def export_to_json(filename, data):
    """
    Exports given data list to JSON file.
    """
    logger.info("Exporting %s to JSON file.", filename)
    with open(f"../json/{filename}.json", "w+", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False, indent=4))
        logger.info("%s exported to json/%s.json successfully!", data, filename)

if __name__ == "__main__":
    main()