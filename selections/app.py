import streamlit as st
from selections import Selections
from grade_assignment import GradeAssignment
from results import Results


def todo(*args):
    st.title("App to do list")

    st.subheader("Selections")
    st.write("- Update/Create teams. 50% done. TODO: Create teams.")
    st.write("- Load / update games")
    st.write(
        """
        - Create locks so selections cant be changed after the game. Manual lock implemented.
        """
    )

    st.write("- DONE: Create results page.")
    st.write("- DONE: Create weekly selection summary")
    st.write("- DONE: Allow for multiple games per week per team.")

    st.subheader("Databases")
    st.write("- Add users to track who made a change")
    st.write("- Research db writing concurrency")


apps = {
    "TODO:": todo,
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
    apps[app_name](database_lock, season)
