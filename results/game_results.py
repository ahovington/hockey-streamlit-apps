from typing import Optional
import streamlit as st
import datetime as dt
import pandas as pd

from utils import read_data


def GameResults() -> None:
    """Display game results

    Retuns: None
    """
    _, col2, col3, col4, _ = st.columns([3, 2, 2, 2, 1])
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
        st.dataframe(game_results, hide_index=True, use_container_width=True)

    centered_text = (
        lambda x, s: f"""<h{s} style='text-align: center; color: black;'>{ x }</h{s}>"""
    )
    title_size = 6
    metric_size = 4
    for _, row in game_results.iterrows():
        with st.container(border=True):
            # col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns(
            #     [1, 0.1, 1, 1, 1, 2, 1, 1, 1, 0.1]
            # )
            col1, col2, col3, col5, col7, col9, _ = st.columns(
                [1, 0.05, 1, 1, 1, 1, 0.05]
            )
            with col1.container():
                st.write("")
                co1, col2 = st.columns([1, 1])

                if not game_round:
                    co1.markdown(
                        centered_text("Round", title_size), unsafe_allow_html=True
                    )
                    co1.markdown(
                        centered_text(row["round"], metric_size), unsafe_allow_html=True
                    )
                if not team:
                    col2.markdown(
                        centered_text("Grade", title_size), unsafe_allow_html=True
                    )
                    col2.markdown(
                        centered_text(row["grade"], metric_size), unsafe_allow_html=True
                    )

            with col3.container():
                st.write("")
                _, middle, _ = st.columns([1, 1, 1])
                middle.image("./assets/wests.png", width=20)
            # with col4.container():
            #     st.write("")
            #     st.markdown(centered_text("Team", title_size), unsafe_allow_html=True)
            #     if not team:
            #         st.markdown(
            #             centered_text(row["team_name"], metric_size),
            #             unsafe_allow_html=True,
            #         )
            #     else:
            #         st.markdown(
            #             centered_text(row["team"], metric_size), unsafe_allow_html=True
            #         )
            with col5.container():
                st.write("")
                st.markdown(
                    centered_text("Goals for", title_size), unsafe_allow_html=True
                )
                st.markdown(
                    centered_text(row["goals_for"], metric_size), unsafe_allow_html=True
                )

            # with col6.container():
            #     st.markdown(
            #         centered_text(row["start_ts"], title_size), unsafe_allow_html=True
            #     )
            #     st.markdown(
            #         centered_text(row["location_name"], title_size),
            #         unsafe_allow_html=True,
            #     )
            #     st.markdown(
            #         centered_text(row["field"], title_size), unsafe_allow_html=True
            #     )
            #     st.write("")

            with col7.container():
                st.write("")
                st.markdown(
                    centered_text("Goals against", title_size), unsafe_allow_html=True
                )
                st.markdown(
                    centered_text(row["goals_against"], metric_size),
                    unsafe_allow_html=True,
                )

            # with col8.container():
            #     st.write("")
            #     st.markdown(
            #         centered_text("Opposition", title_size), unsafe_allow_html=True
            #     )
            #     st.markdown(
            #         centered_text(row["opposition"], metric_size),
            #         unsafe_allow_html=True,
            #     )
            with col9.container():
                st.write("")
                _, middle, _ = st.columns([1, 1, 1])
                middle.image(
                    assets.get(row["opposition"], "./assets/default.jpeg"),
                    width=20,
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
            l.name as location_name,
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
