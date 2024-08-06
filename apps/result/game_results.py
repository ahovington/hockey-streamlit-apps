from dataclasses import dataclass
from typing import Optional
import pandas as pd
import streamlit as st
from streamlit_calendar import calendar

from utils import select_box_query
from config import config
from result.models import team_names, game_rounds, game_results_data


def main() -> None:
    """Display game results"""

    # Filters
    col1, col2, col3, _ = st.columns([2, 2, 2, 2], gap="small")
    config.app.seasons.sort(reverse=True)
    season = select_box_query("Season", config.app.seasons, col1, "Select season...")
    if not season:
        season = config.app.seasons[0]
    team = select_box_query(
        "Team",
        team_names(season).loc[:, "team_name"].values.tolist(),
        col2,
        "Select team...",
    )
    game_round = select_box_query(
        "Round", game_rounds().values.tolist(), col3, "Select round..."
    )

    # Filter to choose how to view the results
    result_views = {
        "Tiles": results_tile,
        "Calendar": results_calendar,
        "Table": results_table,
    }
    col1, _ = st.columns([4, 4], gap="small")
    view = col1.selectbox("Results layout", ["Tiles", "Calendar", "Table"])

    show_applied_filters(season=season, team=team, round=game_round)

    game_results = load_game_results(season=season, team=team, game_round=game_round)
    if not game_results:
        st.warning(f"""No games results found.""")
        return

    result_views.get(view, "Tiles")(game_results)


@dataclass
class Game:
    team: str
    round: str
    grade: str
    location: str
    field: str
    start_time: str
    team_logo_url: str
    opposition_team: str
    opposition_team_logo_url: str
    goals_for: int
    goals_against: int
    result: str

    def to_dict(self):
        return {
            "team": self.team,
            "round": self.round,
            "grade": self.grade,
            "location": self.location,
            "field": self.field,
            "start_time": self.start_time,
            "team_logo_url": self.team_logo_url,
            "opposition_team": self.opposition_team,
            "opposition_team_logo_url": self.opposition_team_logo_url,
            "goals_for": self.goals_for,
            "goals_against": self.goals_against,
            "result": self.result,
        }


def load_game_results(season: str, team: str, game_round: str) -> Optional[list[Game]]:
    game_results = game_results_data(season, team, game_round)
    if not game_results.shape[0]:
        return
    games = []
    for _, game in game_results.iterrows():
        games += [
            Game(
                round=str(game["round"]),
                grade=game["grade"],
                location=game["location_name"],
                field=game["field"],
                start_time=game["start_ts"],
                team=game["team"],
                team_logo_url=_club_logo_url(game["team"]),
                opposition_team=game["opposition"],
                opposition_team_logo_url=_club_logo_url(game["opposition"]),
                goals_for=game["goals_for"],
                goals_against=game["goals_against"],
                result=game["result"],
            )
        ]
    return games


def results_tile(games: list[Game]):
    """Display results in a tiled view

    args:
        df (pd.DataFrame): Dataframe with the results data.
    """
    # present results
    for game in games:
        if game.opposition_team == "BYE":
            continue
        with st.container(border=True):
            results_layout(
                game.round,
                game.grade,
                game.location,
                game.field,
                game.team_logo_url,
                game.team,
                game.goals_for,
                game.opposition_team_logo_url,
                game.goals_against,
                game.opposition_team,
            )
            st.write("")


def show_applied_filters(**kwargs):
    """Pass the filters applied and print as a formatted string"""
    filters_applied = []
    for k, v in kwargs.items():
        if v:
            filters_applied.append(f"{k}: {v}")
    st.subheader(
        f"""Game Results for { ", ".join(filters_applied) }""",
        divider="green",
    )


def results_layout(
    round: str,
    grade: str,
    location: str,
    field: str,
    image1_url: str,
    team1_name: str,
    team1_score: int,
    image2_url: str,
    team2_score: int,
    team2_name: str,
):
    return st.markdown(
        f"""
        <div style="text-align: center; line-height: 1.0;">
            <p style="font-size: 18px;"><strong>Round {round} - {grade} Grade</strong></p>
        </div>
        <div style="text-align: center; line-height: 1.0;">
            <p style="font-size: 18px;"><strong>{location} - {field} field</strong></p>
        </div>
        <div style="display: flex; justify-content: space-around; align-items: center; line-height: 1.0;">
            <div style="text-align: center;">
                <img src="{image1_url}" alt="West Team" width="100">
                <p></p>
                <p>{team1_name}</p>
            </div>
            <div style="text-align: center;">
                <p><strong><span style="font-size: 36px;">{team1_score}</strong></p>
            </div>
            <div style="text-align: center;">
                <p><strong><span style="font-size: 36px;"> - </strong></p>
            </div>
            <div style="text-align: center;">
                <p><strong><span style="font-size: 36px;">{team2_score}</strong></p>
            </div>
            <div style="text-align: center;">
                <img src="{image2_url}" alt="Opposition" width="100">
                <p></p>
                <p>{team2_name}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def results_calendar(games: list[Game]):
    """Display results in a calendar list

    args:
        df (pd.DataFrame): Dataframe with the results data.
    """
    result = {"win": "#359e23", "loss": "#a81919", "draw": "#ded70d"}

    game_events = []
    for game in games:
        game_events.append(
            {
                "title": (
                    "Round "
                    + game.round
                    + ": "
                    + game.grade
                    + " vs "
                    + game.opposition_team
                ),
                "color": result.get(game.result),
                "start": str(game.start_time),
                "end": str(game.start_time + pd.DateOffset(hours=1)),
            }
        )
    cal_options = {
        "initialDate": str(max([game.start_time for game in games])),
        "initialView": "listMonth",
    }
    _calendar_config(game_events, cal_options)


def _calendar_config(events: dict, options: dict):
    calendar(
        events=events,
        options=options,
        custom_css="""
            .fc-event-past {
                opacity: 0.8;
            }
            .fc-event-time {
                font-style: italic;
            }
            .fc-event-title {
                font-weight: 700;
            }
            .fc-toolbar-title {
                font-size: 2rem;
            }   
            """,
    )


def results_table(games: list[Game]) -> None:
    """Display results in a table

    args:
        games: A list of Games.
    """
    _results = pd.DataFrame.from_records(
        [game.to_dict() for game in games],
        exclude=["team_logo_url", "opposition_team_logo_url"],
    )
    st.dataframe(_results, hide_index=True, use_container_width=True)


def _club_logo_url(team_name: str) -> str:
    """Find the club name in the team name.

    Args:
        team_name (str): The raw team name.

    Returns:
        str: The url to the team logo.
    """
    _team_name = team_name.upper()
    clean_name = ""
    if "WEST" in _team_name:
        clean_name = "West"
    if "UNI" in _team_name:
        clean_name = "University"
    if "TIGER" in _team_name:
        clean_name = "Tigers"
    if "SOUTH" in _team_name:
        clean_name = "Souths"
    if "UNI" in _team_name:
        clean_name = "University"
    if "PORT" in _team_name:
        clean_name = "Port Stephens"
    if "NORTH" in _team_name:
        clean_name = "Norths"
    if "MAITLAND" in _team_name:
        clean_name = "Maitland"
    if "GOSFORD" in _team_name:
        clean_name = "Gosford"
    if "CRUSADER" in _team_name:
        clean_name = "Crusaders"
    if "COLT" in _team_name:
        clean_name = "Colts"
    return config.app.logo_assets.get(clean_name)


main()
