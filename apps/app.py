import streamlit as st
from dotenv import load_dotenv
from pathlib import Path

from config import config
from auth import logout

load_dotenv(dotenv_path=Path(".env"))

results_path = Path("result")
results_game = st.Page(
    page=results_path / "game_results.py",
    title="Game Results",
    icon=":material/emoji_events:",
    default=True,
)
results_team = st.Page(
    page=results_path / "team_results.py",
    title="Team Results",
    icon=":material/emoji_events:",
)
results_player = st.Page(
    page=results_path / "player_profile.py",
    title="Player Profile",
    icon=":material/emoji_events:",
)

selections_path = Path("selection")
selections_games = st.Page(
    page=selections_path / "games.py",
    title="Enter Games",
    icon=":material/person_add:",
)
selections_players = st.Page(
    page=selections_path / "selections.py",
    title="Enter Selections",
    icon=":material/person_add:",
)
selections_results = st.Page(
    page=selections_path / "results.py",
    title="Enter Results",
    icon=":material/person_add:",
)

registrations_path = Path("registration")
registrations_summary = st.Page(
    page=registrations_path / "registration_overview.py",
    title="Registration Summary",
    icon=":material/app_registration:",
)
registrations_grade = st.Page(
    page=registrations_path / "grade_assignments.py",
    title="Enter Grade Assignment",
    icon=":material/app_registration:",
)

finance_path = Path("finance")
finance_overview = st.Page(
    page=finance_path / "club_fees_overview.py",
    title="Fees Summary",
    icon=":material/bar_chart:",
)
finance_outstanding = st.Page(
    page=finance_path / "club_fees_outstanding.py",
    title="Fees Outstanding",
    icon=":material/bar_chart:",
)

login_path = Path("login")
login_page = st.Page(
    page=login_path / "login.py",
    title="Login",
    icon=":material/key:",
)
login_create_login = st.Page(
    page=login_path / "create_login.py",
    title="Create Login",
    icon=":material/key:",
)
login_reset_password = st.Page(
    page=login_path / "reset_password.py",
    title="Reset Password",
    icon=":material/key:",
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
        navigation["Login"] = [login_page, login_create_login]
    navigation["Results"] = [results_game, results_team, results_player]
    navigation["Results"] = [results_game, results_team, results_player]
    navigation["Selections"] = [
        selections_games,
        selections_players,
        selections_results,
    ]
    navigation["Registrations"] = [registrations_summary, registrations_grade]
    navigation["Finance"] = [finance_overview, finance_outstanding]
    if st.session_state.get("authentication_status", False):
        navigation["Reset Password"] = [login_reset_password]

    if st.session_state.get("authentication_status", False):
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
