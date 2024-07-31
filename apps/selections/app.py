import streamlit as st

from config import Config
from utils import clean_query_params
from auth import login, register_user, auth
from .documentation import Documentation
from .results import Results
from .selections import Selections
from .games import Games

apps = {
    "Documentation": Documentation,
    "Games": Games,
    "Selections": Selections,
    "Results": Results,
}


def App(config: Config):
    clean_query_params(["Application"])
    with st.sidebar:
        config.app.seasons.sort(reverse=True)
        st.subheader("", divider="green")
        database_lock = st.toggle("Lock database", True)
        season = st.selectbox("Season", config.app.seasons)

    col1, col2 = st.columns([3, 7])
    col1.image(config.app.west_logo_url)
    col2.title("West Hockey Newcastle Selections")

    authenticator = auth(["admin", "committee_member", "team_manager", "selector"])
    if login(authenticator):
        APP_NAME = tuple(apps.keys())[0]
        APP_NAME = col2.selectbox("Select page", list(apps.keys()))
        apps[APP_NAME](config, database_lock, season)
    else:
        with st.expander("Create login"):
            register_user(authenticator)
