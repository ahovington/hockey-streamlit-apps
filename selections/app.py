import streamlit as st
from selections import Selections
from grade_assignment import GradeAssignment
from results import Results


def documentation(*args):
    st.title("West Hockey Newcastle Selections App")

    st.write("The following pages can be selected from the drop down menu above.")

    st.subheader("Grade assignments page", divider="green")
    st.write(
        """
            - Assign each player to a team and a grade.
            - This will help with selections and show up on the players profile.
            - It is the responsibility of the selection committee to update this page.
        """
    )
    st.write("")

    st.subheader("Selections page", divider="green")
    st.write(
        """
            - Select players to play each game.
            - Generate the selections sheet each round.
            - It is the responsibility of the selection committee to update this page.
        """
    )
    st.write("")

    st.subheader("Results page", divider="green")
    st.write(
        """
            - Record the results of each game.
            - Both the overall team and individual results should be recorded.
            - It is the responsibility of the team manager to update this page.
        """
    )
    st.write("")

    st.subheader("", divider="green")
    st.subheader("--- To-do list ---")
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
    "Documentation": documentation,
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
