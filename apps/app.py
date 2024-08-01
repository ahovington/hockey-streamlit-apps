import streamlit as st
from dotenv import load_dotenv
from pathlib import Path

from config import config

# from utils import select_box_query


load_dotenv(dotenv_path=Path(".env"))


results_game = st.Page(
    page="results/game_results.py",
    title="Game Results",
    icon=":material/emoji_events:",
)
results_team = st.Page(
    page="results/team_results.py",
    title="Team Results",
    icon=":material/emoji_events:",
)
results_player = st.Page(
    page="results/player_profile.py",
    title="Player Profile",
    icon=":material/emoji_events:",
)

selections_games = st.Page(
    page="selections/games.py",
    title="Enter Games",
    icon=":material/person_add:",
)
selections_players = st.Page(
    page="selections/selections.py",
    title="Enter Selections",
    icon=":material/person_add:",
)
selections_results = st.Page(
    page="selections/results.py",
    title="Enter Results",
    icon=":material/person_add:",
)

registrations_summary = st.Page(
    page="registrations/registration_overview.py",
    title="Registration Summary",
    icon=":material/app_registration:",
)
registrations_grade = st.Page(
    page="registrations/grade_assignments.py",
    title="Enter Grade Assignment",
    icon=":material/app_registration:",
)

finance_overview = st.Page(
    page="finance/club_fees_overview.py",
    title="Fees Summary",
    icon=":material/bar_chart:",
)
finance_outstanding = st.Page(
    page="finance/club_fees_outstanding.py",
    title="Fees Outstanding",
    icon=":material/bar_chart:",
)

if __name__ == "__main__":
    st.set_page_config(
        page_title="Newcastle West Hockey",
        page_icon=config.app.club_logo,
        layout="wide",
        initial_sidebar_state="auto",
    )

    pg = st.navigation(
        {
            "Results": [results_game, results_team, results_player],
            "Selections": [selections_games, selections_players, selections_results],
            "Registrations": [registrations_summary, registrations_grade],
            "Finance": [finance_overview, finance_outstanding],
        }
    )

    st.logo(config.app.club_logo)
    col1, col2 = st.columns([1, 6], vertical_alignment="center", gap="medium")
    col1.image(config.app.club_logo, use_column_width=True)
    col2.title(
        config.app.club_name + " Hockey Club",
    )
    st.sidebar.text("Maintained by Alastair 🧑🏻‍💻")

    pg.run()

    # with st.sidebar:
    #     app_name = select_box_query("Application", tuple(apps.keys()), st)
    # apps[app_name](config)
