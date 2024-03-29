import streamlit as st

from utils import config, clean_query_params
from auth import auth, login, register_user
from .club_fees_outstanding import ClubFeesOustanding
from .club_fees_overview import ClubFeesOverview

apps = {
    "Club Fees Overdue": ClubFeesOustanding,
    "Club Fees Overview": ClubFeesOverview,
}


def App():
    clean_query_params(["Application"])
    col1, col2 = st.columns([3, 7])
    col1.image(config.app.west_logo_url)
    col2.title("West Hockey Newcastle Club Fees")

    authenticator = auth(["admin", "committee_member", "collector"])
    if login(authenticator):
        APP_NAME = tuple(apps.keys())[0]
        APP_NAME = col2.selectbox("Select page", list(apps.keys()))
        apps[APP_NAME]()
    else:
        with st.expander("Create login"):
            register_user(authenticator)
