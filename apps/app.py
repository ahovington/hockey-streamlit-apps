import streamlit as st

from config import config
from auth import logout
from pages import (
    login_pages,
    reset_password_pages,
    finance_pages,
    registrations_pages,
    console_pages,
)


if __name__ == "__main__":
    st.set_page_config(
        page_title="Newcastle West Hockey",
        page_icon=config.app.club_logo,
        layout="wide",
        initial_sidebar_state="auto",
    )

    navigation: dict[str : list[st.Page]] = {}
    if not st.session_state.get("authentication_status", False):
        navigation["Login"] = login_pages
    navigation["Registrations"] = registrations_pages
    navigation["Finance"] = finance_pages
    if st.session_state.get("authentication_status", False):
        navigation["Reset Password"] = reset_password_pages
        logout()

    pg = st.navigation(navigation)
    st.logo(config.app.club_logo)
    col1, col2 = st.columns([1, 6], vertical_alignment="center", gap="medium")
    col1.image(config.app.club_logo, use_column_width=False, width=100)
    col2.title(
        config.app.club_name + " Hockey Club",
    )
    st.sidebar.text("Maintained by Alastair 🧑🏻‍💻")

    pg.run()
