from typing import Optional
import pandas as pd
import streamlit as st
from streamlit_calendar import calendar

from utils import assets, config, read_data, select_box_query, clean_query_params


def GameResults() -> None:
    """Display game results"""
    clean_query_params(["Application", "page", "Season", "Team", "Round"])

    _, col2, col3, col4, _ = st.columns([3, 2, 2, 2, 1], gap="small")
    config.app.seasons.sort(reverse=True)
    season = select_box_query("Season", config.app.seasons, col2, "Select season...")
    if not season:
        season = config.app.seasons[0]
    team = select_box_query(
        "Team",
        read_data(
            f"""
            select
                distinct
                team || ' - ' || grade as team_name,
                team_order
            from teams
            where
                season = '{season}'
            order by
                team_order
        """
        )
        .loc[:, "team_name"]
        .values.tolist(),
        col3,
        "Select team...",
    )
    game_round = select_box_query("Round", round_filter_data(), col4, "Select round...")

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


def round_filter_data():
    df = read_data(
        """
        select
            distinct
            round,
            case
                when round = 'SF1' then '30'
                when round = 'PF1' then '40'
                when round = 'GF1' then '30'
                else round
            end as round_order
        from games
        """
    )
    df.loc[:, "round_order"] = df.loc[:, "round_order"].astype(float)
    df = df.sort_values("round_order")["round"]
    return df.values.tolist()


def game_results_data(
    season: str, team: Optional[str] = None, game_round: Optional[str] = None
) -> pd.DataFrame:
    """Extact the outstanding club fees.

    Args:
        season (str): The hockey season, usually the calendar year.
        team (str, optional): The teams name.
        game_round (str, optional): The round of the season.

    Retuns:
        pd.DataFrame: The results of the query.
    """
    filters = ["where", f"g.season = '{ season }'"]
    if team:
        filters.append("and")
        filters.append(f"t.team || ' - ' || t.grade = '{ team }'")
    if game_round:
        filters.append("and")
        filters.append(f"g.round = '{ game_round }'")
    df = read_data(
        f"""
        select
            g.id,
            t.team,
            t.grade,
            t.team || ' - ' || t.grade as team_name,
            g.season,
            g.round,
            case
                when l.name = 'Newcastle International Hockey Centre'
                then 'NIHC'
                else l.name
            end as location_name,
            l.field,
            g.finals,
            case
                when g.opposition = '4thGreen' then 'West Green'
                when g.opposition = '4thRed' then 'West Red'
                else g.opposition 
            end as opposition,
            g.start_ts,
            g.goals_for,
            g.goals_against,
            case
                when g.goals_for > g.goals_against then 'win'
                when g.goals_for < g.goals_against then 'loss'
                when g.goals_for = g.goals_against then 'draw'
            end as result,
            g.goals_for > g.goals_against as win,
            g.goals_for < g.goals_against as loss,
            g.goals_for = g.goals_against as draw
        from games as g
        left join teams as t
        on g.team_id = t.id
        left join locations as l
        on g.location_id = l.id
        { " ".join(filters) }
        order by
            t.team_order,
            g.start_ts
        """
    )
    df.loc[:, "goals_for"] = (
        df.loc[:, "goals_for"].replace("", 0).astype(float).astype(int)
    )
    df.loc[:, "goals_against"] = (
        df.loc[:, "goals_against"].replace("", 0).astype(float).astype(int)
    )
    return df


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
                assets.get(row["team"]),
                row["team"],
                row["goals_for"],
                assets.get(row["opposition"]),
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
