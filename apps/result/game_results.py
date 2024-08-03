from typing import Optional
import pandas as pd
import streamlit as st
from streamlit_calendar import calendar

from utils import select_box_query, team_name_clean
from config import config
from result.models import team_names, game_rounds, game_results_data


def main() -> None:
    """Display game results"""

    _, col2, col3, col4, _ = st.columns([3, 2, 2, 2, 1], gap="small")
    config.app.seasons.sort(reverse=True)
    season = select_box_query("Season", config.app.seasons, col2, "Select season...")
    if not season:
        season = config.app.seasons[0]
    team = select_box_query(
        "Team",
        team_names(season).loc[:, "team_name"].values.tolist(),
        col3,
        "Select team...",
    )
    game_round = select_box_query(
        "Round", game_rounds().values.tolist(), col4, "Select round..."
    )

    # Show filters applied
    filters_applied = []
    if season:
        filters_applied.append(f"Season: { season }")
    if team:
        filters_applied.append(f"Team: { team }")
    if game_round:
        filters_applied.append(f"Round: { game_round }")
    st.subheader(
        f"""Game Results for { ", ".join(filters_applied) }""",
        divider="green",
    )

    # load data
    game_results = game_results_data(season, team, game_round)

    if not game_results.shape[0]:
        st.warning(f"""No results found for { ", ".join(filters_applied) }""")
        return

    result_views = {
        "Tiles": results_tile,
        "Calendar": results_calendar,
        "Table": results_table,
    }

    _, col2 = st.columns([3, 7], gap="small")
    view = col2.selectbox("Results layout", ["Tiles", "Calendar", "Table"])

    result_views.get(view, "Tiles")(game_results)


def results_tile(df: pd.DataFrame):
    """Display results in a tiled view

    args:
        df (pd.DataFrame): Dataframe with the results data.
    """
    # present results
    for _, row in df.iterrows():
        if row["opposition"] == "BYE":
            continue
        with st.container(border=True):
            results_layout(
                row["round"],
                row["grade"],
                row["location_name"],
                row["field"],
                config.app.logo_assets.get(team_name_clean(row["team"])),
                row["team"],
                row["goals_for"],
                config.app.logo_assets.get(team_name_clean(row["opposition"])),
                row["goals_against"],
                row["opposition"],
            )
            st.write("")


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
            <p style="font-size: 18px;"><strong>Round { round } - { grade } Grade</strong></p>
        </div>
        <div style="text-align: center; line-height: 1.0;">
            <p style="font-size: 18px;"><strong>{ location } - { field } field</strong></p>
        </div>
        <div style="display: flex; justify-content: space-around; align-items: center; line-height: 1.0;">
            <div style="text-align: center;">
                <img src="{ image1_url }" alt="West Team" width="100">
                <p></p>
                <p>{ team1_name }</p>
            </div>
            <div style="text-align: center;">
                <p><strong><span style="font-size: 36px;">{ team1_score }</strong></p>
            </div>
            <div style="text-align: center;">
                <p><strong><span style="font-size: 36px;"> - </strong></p>
            </div>
            <div style="text-align: center;">
                <p><strong><span style="font-size: 36px;">{ team2_score }</strong></p>
            </div>
            <div style="text-align: center;">
                <img src="{ image2_url }" alt="Opposition" width="100">
                <p></p>
                <p>{ team2_name }</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def results_calendar(df: pd.DataFrame):
    """Display results in a calendar list

    args:
        df (pd.DataFrame): Dataframe with the results data.
    """
    result = {"win": "#359e23", "loss": "#a81919", "draw": "#ded70d"}

    game_events = []
    for _, row in df.iterrows():
        game_events.append(
            {
                "title": (
                    "Round "
                    + row["round"]
                    + ": "
                    + row["grade"]
                    + " vs "
                    + row["opposition"]
                ),
                "color": result.get(row["result"]),
                "start": str(row["start_ts"]),
                "end": str(row["start_ts"] + pd.DateOffset(hours=1)),
            }
        )
    cal_options = {
        "initialDate": str(max(df["start_ts"])),
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


def results_table(df: pd.DataFrame):
    """Display results in a table

    args:
        df (pd.DataFrame): Dataframe with the results data.
    """
    _results = df.drop(columns=["id", "team", "grade", "finals", "win", "loss", "draw"])
    st.dataframe(_results, hide_index=True, use_container_width=True)


main()
