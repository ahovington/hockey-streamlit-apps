import pandas as pd
import streamlit as st

from config import Config
from utils import read_data, select_box_query, clean_query_params


def TeamResults(config: Config) -> None:
    """Display game results"""
    clean_query_params(["Application", "Page", "Season"])

    _, col2, _, _, _ = st.columns([3, 2, 2, 2, 1], gap="small")
    season = select_box_query("Season", config.app.seasons, col2, "Select season...")
    if not season:
        st.warning("Pick a season from dropdown.")
        return

    st.subheader(
        f"""West Team Results for { season }""",
        divider="green",
    )

    team_results = team_results_data(season)
    if not team_results.shape[0]:
        st.warning(f"No results found for season { season }")
        return

    for _, row in team_results.iterrows():
        with st.container(border=True):
            team_layout(
                row["team_name"],
                row["games_played"],
                row["win"],
                row["loss"],
                row["draw"],
                (row["win"] * 2 + row["draw"]),
            )
            with st.expander("More detail"):
                team_detail_layout(
                    row["goals_for"],
                    row["goals_against"],
                    (row["goals_for"] - row["goals_against"]),
                    f"""{ (row["win"] * 2 + row["draw"]) / (row["games_played"] * 2) :.1%}""",
                )

                st.warning("Not fully implemented")
                st.write("Top Goal Scorers")
                # Data for the table (replace with your actual data)
                data = [
                    {"Name": "John Doe", "Goals": 15},
                    {"Name": "Jane Smith", "Goals": 12},
                    # Add more rows as needed
                ]
                st.table(data)

                st.write("Most Points")
                # Data for the table (replace with your actual data)
                data = [
                    {"Name": "John Doe", "Points": 15},
                    {"Name": "Jane Smith", "Points": 12},
                    # Add more rows as needed
                ]
                st.table(data)


def team_layout(
    team_name: str,
    games_played: int,
    wins: int,
    losses: int,
    draws: int,
    points: int,
    title_size: int = 16,
    metric_size: int = 32,
):
    return st.markdown(
        f"""
        <div style="text-align: center; line-height: 1.0;">
            <p style="font-size: 18px;"><strong>{ team_name } Grade</strong></p>
        </div>
        <div style="display: flex; justify-content: space-around; align-items: center; line-height: 1.0;">
            <div style="text-align: center;">
                <p><span style="font-size: { title_size }px;">Games</p>
                <p><strong><span style="font-size: { metric_size }px;">{ games_played }</strong></p>
            </div>
            <div style="text-align: center;">
                <p><span style="font-size: { title_size }px;">Wins</p>
                <p><strong><span style="font-size: { metric_size }px;">{ wins }</strong></p>
            </div>
            <div style="text-align: center;">
                <p><span style="font-size: { title_size }px;">Losses</p>
                <p><strong><span style="font-size: { metric_size }px;">{ losses }</strong></p>
            </div>
            <div style="text-align: center;">
                <p><span style="font-size: { title_size }px;">Draws</p>
                <p><strong><span style="font-size: { metric_size }px;">{ draws }</strong></p>
            </div>
            <div style="text-align: center;">
                <p><span style="font-size: { title_size }px;">Points</p>
                <p><strong><span style="font-size: { metric_size }px;">{ points }</strong></p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def team_detail_layout(
    goals_for: int,
    goals_againt: int,
    goal_difference: int,
    points_percentage: str,
    title_size=12,
    metric_size=24,
):
    return st.markdown(
        f"""
        <div style="display: flex; justify-content: space-around; align-items: center; line-height: 1.0;">
            <div style="text-align: center;">
                <p><span style="font-size: { title_size }px;">Goals for</p>
                <p><strong><span style="font-size: { metric_size }px;">{ goals_for }</strong></p>
            </div>
            <div style="text-align: center;">
                <p><span style="font-size: { title_size }px;">Goals against</p>
                <p><strong><span style="font-size: { metric_size }px;">{ goals_againt }</strong></p>
            </div>    
            <div style="text-align: center;">
                <p><span style="font-size: { title_size }px;">Goal difference</p>
                <p><strong><span style="font-size: { metric_size }px;">{ goal_difference }</strong></p>
            </div>
            <div style="text-align: center;">
                <p><span style="font-size: { title_size }px;">Points percentage</p>
                <p><strong><span style="font-size: { metric_size }px;">{ points_percentage }</strong></p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def team_results_data(season: str) -> pd.DataFrame:
    """Extact the outstanding club fees.

    Args:
        season (str): The hockey season, usually the calendar year.
        team (str, optional): The teams name.
        game_round (str, optional): The round of the season.

    Retuns:
        pd.DataFrame: The results of the query.
    """
    df = read_data(
        # TODO: filter out upcoming games
        f"""
        with game_data as (
            select
                g.id,
                t.team_order,
                t.team,
                t.grade,
                t.team || ' - ' || t.grade as team_name,
                g.season,
                g.goals_for,
                g.goals_against,
                g.goals_for > g.goals_against as win,
                g.goals_for < g.goals_against as loss,
                g.goals_for = g.goals_against as draw
            from games as g
            left join teams as t
            on g.team_id = t.id
            where g.season = '{ season }'
        )

        select
            team_order,
            team,
            grade,
            team_name,
            goals_for,
            goals_against,
            1 as games_played,
            win,
            loss,
            draw
        from game_data as gd
        """
    )
    df.loc[:, "goals_for"] = (
        df.loc[:, "goals_for"].replace("", 0).astype(float).astype(int)
    )
    df.loc[:, "goals_against"] = (
        df.loc[:, "goals_against"].replace("", 0).astype(float).astype(int)
    )
    df = (
        df.groupby(["team_order", "team", "grade", "team_name"])
        .agg(
            {
                "games_played": "sum",
                "goals_for": "sum",
                "goals_against": "sum",
                "win": "sum",
                "loss": "sum",
                "draw": "sum",
            }
        )
        .reset_index()
    )

    return df
