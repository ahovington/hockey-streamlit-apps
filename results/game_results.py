from typing import Optional
import pandas as pd
import streamlit as st

from utils import read_data, assets


def GameResults() -> None:
    """Display game results

    Retuns: None
    """
    _, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1], gap="small")
    season = col2.selectbox("Season", ["2023", "2024"], placeholder="Select season...")
    team = col3.selectbox(
        "Team",
        read_data(
            "select team || ' - ' || grade as team from teams order by team_order"
        ),
        index=None,
        placeholder="Select team...",
    )
    game_round = col4.selectbox(
        "Round",
        round_filter_data(),
        index=None,
        placeholder="Select round...",
    )
    if not season:
        st.warning("Pick a season from dropdown.")
        return

    if not team and not game_round:
        st.warning("Pick either a team or round from dropdown.")
        return

    # Show filters applied
    filters_applied = []
    if game_round:
        filters_applied.append(f"Round: { game_round }")
    if team:
        filters_applied.append(f"Team: { team }")
    st.subheader(
        f"""{ season } Game Results for { ", ".join(filters_applied) }""",
        divider="green",
    )

    # load data
    game_results = game_results_data(season, team, game_round)

    if not game_results.shape[0]:
        st.warning(f"""No results found for for { ", ".join(filters_applied) }""")
        return

    # show raw results table
    with st.expander("Show full results table", expanded=False):
        _results = game_results.drop(columns=["id", "team", "grade", "finals"])
        st.dataframe(_results, hide_index=True, use_container_width=True)

    # present results
    for _, row in game_results.iterrows():
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
    return df.sort_values("round_order")["round"]


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
            g.round
        """
    )
    df.loc[:, "goals_for"] = (
        df.loc[:, "goals_for"].replace("", 0).astype(float).astype(int)
    )
    df.loc[:, "goals_against"] = (
        df.loc[:, "goals_against"].replace("", 0).astype(float).astype(int)
    )
    return df
