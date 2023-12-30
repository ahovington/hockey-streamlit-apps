import streamlit as st
from auth import login_page
from documentation import Documentation
from selections import Selections
from grade_assignment import GradeAssignment
from results import Results

apps = {
    "Documentation": Documentation,
    "Grade Assignments": GradeAssignment,
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
    app_name = tuple(apps.keys())[0]
    app_name = col2.selectbox("Select page", tuple(apps.keys()))

    if login_page():
        apps[app_name](database_lock, season)
