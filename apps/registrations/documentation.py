import streamlit as st


def Documentation(*args):
    """
    Write the documentation for the application.
    """
    st.title("Documentation")

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
