import streamlit as st


def Documentation(*args):
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
