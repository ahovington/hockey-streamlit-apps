import streamlit as st

from utils import read_data, results_data, assets


def GameResults() -> None:
    """Display game results

    Retuns: None
    """
    _, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1], gap="small")
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

    with st.expander("Show full results table", expanded=False):
        _results = game_results.drop(columns=["id", "team", "grade", "finals"])
        st.dataframe(_results, hide_index=True, use_container_width=True)

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
    team1_name: int,
    team1_score: int,
    image2_url: str,
    team2_score,
    team2_name,
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
