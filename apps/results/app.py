import streamlit as st

from utils import config, select_box_query
from .game_results import GameResults
from .team_results import TeamResults
from .player_results import PlayerResults


PAGES = {
    "Game results": GameResults,
    "Team results": TeamResults,
    "Player Statistics": PlayerResults,
}


def App():
    col1, col2 = st.columns([3, 7])
    col1.image(config.app.west_logo_url)
    col2.title("West Hockey Results")
    selected_page = select_box_query("page", list(PAGES.keys()), col2)
    PAGES[selected_page]()
