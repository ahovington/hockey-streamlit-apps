import streamlit as st

from utils import config
from game_results import GameResults
from team_results import TeamResults


apps = {"Game results": GameResults, "Team results": TeamResults}

if __name__ == "__main__":
    st.set_page_config(
        page_title="Results App Newcastle West Hockey",
        page_icon=config.app.west_logo_url,
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    col1, col2 = st.columns([3, 7])
    col1.image(config.app.west_logo_url)
    col2.title("West Hockey Results")

    APP_NAME = tuple(apps.keys())[0]
    APP_NAME = col2.selectbox("Select page", tuple(apps.keys()))
    apps[APP_NAME]()
