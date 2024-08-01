import streamlit as st

from config import config
from utils import select_box_query
from .game_results import GameResults
from .team_results import TeamResults
from .player_profile import PlayerProfile


PAGES = {
    "Game results": GameResults,
    "Team results": TeamResults,
    "Player profile": PlayerProfile,
}


def main():
    col1, col2 = st.columns([3, 7])
    col2.title("West Hockey Results")
    selected_page = select_box_query("Page", list(PAGES.keys()), col2)
    PAGES[selected_page](config)


if __name__ == "__main__":
    main()
