import streamlit as st

from utils import config, clean_query_params
from auth import auth, login, register_user
from .documentation import Documentation
from .grade_assignments import GradeAssignments

apps = {
    "Documentation": Documentation,
    "Registrations Overview": Documentation,
    "Grade Assignment": GradeAssignments,
}


def App():
    clean_query_params(["Application"])
    with st.sidebar:
        st.subheader("", divider="green")
        database_lock = st.toggle("Lock database", True)
        season = st.selectbox("Season", config.app.seasons)

    col1, col2 = st.columns([3, 7])
    col1.image(config.app.west_logo_url)
    col2.title("West Hockey Newcastle Registrations")

    authenticator = auth(["admin", "committee_member"])
    if login(authenticator):
        APP_NAME = tuple(apps.keys())[0]
        APP_NAME = col2.selectbox("Select page", list(apps.keys()))
        apps[APP_NAME](database_lock, season)
    else:
        with st.expander("Create login"):
            register_user(authenticator)
