import streamlit as st

from utils import config
from auth import login, register_user, auth
from documentation import Documentation
from grade_assignments import GradeAssignments
from results import Results
from selections import Selections
from games import Games

apps = {
    "Documentation": Documentation,
    "Grade Assignments": GradeAssignments,
    "Selections": Selections,
    "Results": Results,
    # "Games": Games,
}
if __name__ == "__main__":
    st.set_page_config(
        page_title="Selections App West Hockey Newcastle",
        page_icon=config.app.west_logo_url,
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    with st.sidebar:
        database_lock = st.toggle("Lock database", True)
        season = st.selectbox("Season", ["2023", "2024"])

    col1, col2 = st.columns([3, 7])
    col1.image(config.app.west_logo_url)
    col2.title("West Hockey Newcastle Selections")

    authenticator = auth()
    if login(authenticator):
        APP_NAME = tuple(apps.keys())[0]
        APP_NAME = col2.selectbox("Select page", tuple(apps.keys()))
        apps[APP_NAME](database_lock, season)
    else:
        with st.expander("Create login"):
            register_user(authenticator)
