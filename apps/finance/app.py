import streamlit as st

from config import Config
from utils import clean_query_params, select_box_query
from auth import auth, login, register_user
from .club_fees_outstanding import ClubFeesOustanding
from .club_fees_overview import ClubFeesOverview

PAGES = {
    "Club Fees Overdue": ClubFeesOustanding,
    "Club Fees Overview": ClubFeesOverview,
}


def App(config: Config):
    col1, col2 = st.columns([3, 7])
    col1.image(config.app.club_logo)
    col2.title("West Hockey Newcastle Club Fees")

    authenticator = auth(["admin", "committee_member", "collector"])
    if login(authenticator):
        PAGE_NAME = tuple(PAGES.keys())[0]
        PAGE_NAME = select_box_query("Page", list(PAGES.keys()), col2)
        PAGES[PAGE_NAME](config)
    else:
        with st.expander("Create login"):
            register_user(authenticator)
