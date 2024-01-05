from typing import Optional
import pandas as pd
import streamlit as st

from utils import read_data


def GameResults() -> None:
    """Display game results

    Retuns: None
    """
    TITLE_SIZE = 6
    METRIC_SIZE = 4
    IMAGE_WIDTH = 60

    _, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
    season = col2.selectbox("Season", ["2023", "2024"], placeholder="Select season...")
    team = col3.selectbox(
        "Team",
        read_data("select team || ' - ' || grade from teams"),
        index=None,
        placeholder="Select team...",
    )
    game_round = col4.selectbox(
        "Round",
        read_data("select distinct round from games"),
        index=None,
        placeholder="Select round...",
    )
    html_text_colour = col5.selectbox("Table text colour", ["black", "white"])
    if not season:
        st.warning("Pick a season from dropdown.")
        return
    if not team and not game_round:
        st.warning("Pick either a team or round from dropdown.")
        return

    filters_applied = []
    if game_round:
        filters_applied.append(f"Round: { game_round }")
    if team:
        filters_applied.append(f"Team: { team }")
    st.subheader(
        f"""{ season } Game Results for { ", ".join(filters_applied) }""",
        divider="green",
    )

    game_results = results_data(season, team, game_round)

    assets = {
        "4thGreen": "./assets/wests.png",
        "4thRed": "./assets/wests.png",
        "Port Stephens": "./assets/port_stephens.jpeg",
        "Souths": "./assets/souths.jpeg",
        "Tigers": "./assets/tigers.png",
        "Tiger": "./assets/tigers.png",
        "Maitland": "./assets/maitland.png",
        "University": "./assets/university.jpeg",
        "University Trains": "./assets/university.jpeg",
        "Norths Dark": "./assets/norths.jpeg",
        "Norths Light": "./assets/norths.jpeg",
        "Norths": "./assets/norths.jpeg",
        "North": "./assets/norths.jpeg",
        "Gosford": "./assets/gosford.png",
        "Crusaders": "./assets/crusaders.png",
        "Colts": "./assets/colts.png",
    }

    with st.expander("Show full results table", expanded=False):
        _results = game_results.drop(columns=["team", "grade", "finals"])
        st.dataframe(_results, hide_index=True, use_container_width=True)

    centered_text = (
        lambda x, s: f"""<h{s} style='text-align: center; color: { html_text_colour };'>{ x }</h{s}>"""
    )
    for _, row in game_results.iterrows():
        with st.container(border=True):
            _, middle, _ = st.columns(3)
            middle.markdown(
                centered_text(
                    f"""{ row["grade"] } - Round { row["round"] }""", TITLE_SIZE
                ),
                unsafe_allow_html=True,
            )
            col1, col2, col3, col4 = st.columns([1, 0.5, 0.5, 1])

            with col1.container():
                first, middle, last = st.columns(3)
                middle.image(
                    "./assets/wests.png",
                    width=IMAGE_WIDTH
                    # use_column_width=True,
                )
            with col2.container():
                st.markdown(
                    centered_text("Goals for", TITLE_SIZE), unsafe_allow_html=True
                )
                st.markdown(
                    centered_text(row["goals_for"], METRIC_SIZE), unsafe_allow_html=True
                )
            with col3.container():
                st.markdown(
                    centered_text("Goals against", TITLE_SIZE), unsafe_allow_html=True
                )
                st.markdown(
                    centered_text(row["goals_against"], METRIC_SIZE),
                    unsafe_allow_html=True,
                )
            with col4.container():
                _, middle, _ = st.columns(3)
                middle.image(
                    assets.get(row["opposition"], "./assets/default.jpeg"),
                    width=IMAGE_WIDTH,
                    # use_column_width=True,
                )


def results_data(
    season: str, team: Optional[str], game_round: Optional[str]
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
    return read_data(
        f"""
        select
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
            g.opposition,
            g.start_ts,
            g.goals_for,
            g.goals_against
        from games as g
        left join teams as t
        on g.team_id = t.id
        left join locations as l
        on g.location_id = l.id
        { " ".join(filters) }
        """
    )
