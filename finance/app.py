import streamlit as st

from utils import config
from auth import auth, login, register_user
from club_fees_outstanding import ClubFeesOustanding
from club_fees_overview import ClubFeesOverview

apps = {
    "Outstanding Club fees": ClubFeesOustanding,
    "Overview": ClubFeesOverview,
}
if __name__ == "__main__":
    st.set_page_config(
        page_title="Finance App Newcastle West Hockey",
        page_icon=config.app.west_logo_url,
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    col1, col2 = st.columns([3, 7])
    col1.image(config.app.west_logo_url)
    col2.title("West Hockey Newcastle Club Fees")

    authenticator = auth()
    if login(authenticator):
        APP_NAME = tuple(apps.keys())[0]
        APP_NAME = col2.selectbox("Select page", tuple(apps.keys()))
        apps[APP_NAME]()
    else:
        with st.expander("Create login"):
            register_user(authenticator)
