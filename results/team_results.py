import pandas as pd
import streamlit as st

from utils import read_data


def TeamResults() -> None:
    """Display game results

    Retuns: None
    """
    _, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1], gap="small")
    season = col2.selectbox("Season", ["2023", "2024"], placeholder="Select season...")
    if not season:
        st.warning("Pick a season from dropdown.")
        return

    st.subheader(
        f"""West Team Results for { season }""",
        divider="green",
    )

    team_results = team_results_data(season)

    for _, row in team_results.iterrows():
        with st.container(border=True):
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
            col1.metric("Grade", row["grade"])
            col2.metric("Games Played", row["games_played"])
            col3.metric("Wins", row["win"])
            col4.metric("Losses", row["loss"])
            col5.metric("Draws", row["draw"])
            col6.metric(
                "Points",
                f"""{ (row["win"] * 2 + row["draw"])}""",
            )
            col7.metric(
                "Points percentage",
                f"""{ (row["win"] * 2 + row["draw"]) / (row["games_played"] * 2) :.2%}""",
            )
            col8.metric(
                "Goals difference",
                row["goals_for"] - row["goals_against"],
            )
            with st.expander("More detail"):
                st.warning("Not fully yet implemented")
                col1, col2, col3, col4, _ = st.columns(5)
                col1.metric("Goals for", row["goals_for"])
                col2.metric("Goals against", row["goals_against"])
                with col3.container():
                    st.write("Top goal scores")
                    st.write("1. Name, Goals 0")
                    st.write("2. Name, Goals 0")
                    st.write("3. Name, Goals 0")
                with col4.container():
                    st.write("Most games played")
                    st.write("1. Name, Games 0")
                    st.write("2. Name, Games 0")
                    st.write("3. Name, Games 0")


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
