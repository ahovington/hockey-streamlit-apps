import streamlit as st
from pathlib import Path


# Result pages
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
# Selection pages
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
# Registration pages
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
# Finance pages
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
# Login pages
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


login_pages: list[st.Page] = [login_page, login_create_login]
reset_password_pages: list[st.Page] = [login_reset_password]
result_pages: list[st.Page] = [results_game, results_team, results_player]
selections_pages: list[st.Page] = [
    selections_games,
    selections_players,
    selections_results,
]
registrations_pages: list[st.Page] = [registrations_summary, registrations_grade]
finance_pages: list[st.Page] = [finance_overview, finance_outstanding]
