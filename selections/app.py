import streamlit as st

from auth import login
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
        page_title="Newcastle West Hockey Selections App",
        page_icon="https://cdn.revolutionise.com.au/cups/whc/files/ptejzkfy3k8qvtlg.ico",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    with st.sidebar:
        database_lock = st.toggle("Lock database", True)
        season = st.selectbox("Season", ["2023", "2024"])

    col1, col2 = st.columns([2, 3])
    col1.image("./rosella.png")

    if login():
        APP_NAME = tuple(apps.keys())[0]
        APP_NAME = col2.selectbox("Select page", tuple(apps.keys()))
        apps[APP_NAME](database_lock, season)

    # implement with db
    # else:
    #     with st.expander("Create login"):
    #         register_user()
