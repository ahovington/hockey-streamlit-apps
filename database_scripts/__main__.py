from sqlalchemy.orm import Session

from common.config import config
from db import engine
from .locations import Locations
from .teams import Teams
from .games import Games
from .selections import Selections

LOCATIONS_SOURCE_DATA_FILENAME = "locations.csv"
TEAMS_SOURCE_DATA_FILENAME = "teams.csv"
GAMES_SOURCE_DATA_FILENAME = "games.csv"
SELECTIONS_SOURCE_DATA_FILENAME = "selections.csv"
SOURCE_LOCATION = lambda x: f"data/{config.year}/{x}"

session = Session(engine)

location = Locations(session, SOURCE_LOCATION(LOCATIONS_SOURCE_DATA_FILENAME))
team = Teams(session, SOURCE_LOCATION(TEAMS_SOURCE_DATA_FILENAME))
game = Games(session, SOURCE_LOCATION(GAMES_SOURCE_DATA_FILENAME))
selection = Selections(session, SOURCE_LOCATION(SELECTIONS_SOURCE_DATA_FILENAME))


def load_all_sources():
    location.load()
    team.load()
    game.load()
    selection.load()


def update_all_sources():
    location.update()
    team.update()
    game.update()
    selection.update()


if __name__ == "__main__":
    load_all_sources()
    update_all_sources()
