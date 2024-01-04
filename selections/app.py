import streamlit as st

from auth import login, register_user, auth
from documentation import Documentation
from grade_assignments import GradeAssignments
from results import Results
from selections import Selections

apps = {
    "Documentation": Documentation,
    "Grade Assignments": GradeAssignments,
    "Selections": Selections,
    "Results": Results,
}
if __name__ == "__main__":
    st.set_page_config(
        page_title="Selections App West Hockey Newcastle",
        page_icon="https://cdn.revolutionise.com.au/cups/whc/files/ptejzkfy3k8qvtlg.ico",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    with st.sidebar:
        database_lock = st.toggle("Lock database", True)
        season = st.selectbox("Season", ["2023", "2024"])

    col1, col2 = st.columns([3, 7])
    col1.image("./assets/wests.png")
    col2.title("West Hockey Newcastle Selections")

    authenticator = auth()
    if login(authenticator):
        APP_NAME = tuple(apps.keys())[0]
        APP_NAME = col2.selectbox("Select page", tuple(apps.keys()))
        apps[APP_NAME](database_lock, season)
    else:
        with st.expander("Create login"):
            register_user(authenticator)
