from typing import Optional
import pandas as pd
import streamlit as st

from utils import read_data


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
    game_results.loc[:, "goals_for"] = game_results.loc[:, "goals_for"].replace("", 0)
    game_results.loc[:, "goals_against"] = game_results.loc[:, "goals_against"].replace(
        "", 0
    )

    assets = {
        "4thGreen": "https://cdn.revolutionise.com.au/logos/tqbgdyotasa2pwz4.png",
        "4thRed": "https://cdn.revolutionise.com.au/logos/tqbgdyotasa2pwz4.png",
        "West Green": "https://cdn.revolutionise.com.au/logos/tqbgdyotasa2pwz4.png",
        "West Red": "https://cdn.revolutionise.com.au/logos/tqbgdyotasa2pwz4.png",
        "West": "https://cdn.revolutionise.com.au/logos/tqbgdyotasa2pwz4.png",
        "Port Stephens": "https://cdn.revolutionise.com.au/logos/lilbc4vodqtkx3uq.jpg",
        "Souths": "https://cdn.revolutionise.com.au/logos/ktxvg5solvqxq8yv.jpg",
        "Tigers": "https://cdn.revolutionise.com.au/logos/ksbq9xvnjatt1drb.png",
        "Tiger": "https://cdn.revolutionise.com.au/logos/ksbq9xvnjatt1drb.png",
        "Maitland": "https://cdn.revolutionise.com.au/logos/gfnot4z2fginovwo.png",
        "University": "https://cdn.revolutionise.com.au/logos/3eo6ghaoxwyblbhv.jpg",
        "University Trains": "https://cdn.revolutionise.com.au/logos/3eo6ghaoxwyblbhv.jpg",
        "Norths Dark": "https://scontent-syd2-1.xx.fbcdn.net/v/t39.30808-6/303108111_594953908808882_8195829583102730483_n.jpg?_nc_cat=103&ccb=1-7&_nc_sid=efb6e6&_nc_ohc=3mXcO3Igh1oAX92MBFS&_nc_ht=scontent-syd2-1.xx&oh=00_AfAJideVNofqudUjcWqNERY5ZCgdILdeiG3FHI1F-6V6hg&oe=659D6046",
        "Norths Light": "https://scontent-syd2-1.xx.fbcdn.net/v/t39.30808-6/303108111_594953908808882_8195829583102730483_n.jpg?_nc_cat=103&ccb=1-7&_nc_sid=efb6e6&_nc_ohc=3mXcO3Igh1oAX92MBFS&_nc_ht=scontent-syd2-1.xx&oh=00_AfAJideVNofqudUjcWqNERY5ZCgdILdeiG3FHI1F-6V6hg&oe=659D6046",
        "Norths": "https://scontent-syd2-1.xx.fbcdn.net/v/t39.30808-6/303108111_594953908808882_8195829583102730483_n.jpg?_nc_cat=103&ccb=1-7&_nc_sid=efb6e6&_nc_ohc=3mXcO3Igh1oAX92MBFS&_nc_ht=scontent-syd2-1.xx&oh=00_AfAJideVNofqudUjcWqNERY5ZCgdILdeiG3FHI1F-6V6hg&oe=659D6046",
        "North": "https://scontent-syd2-1.xx.fbcdn.net/v/t39.30808-6/303108111_594953908808882_8195829583102730483_n.jpg?_nc_cat=103&ccb=1-7&_nc_sid=efb6e6&_nc_ohc=3mXcO3Igh1oAX92MBFS&_nc_ht=scontent-syd2-1.xx&oh=00_AfAJideVNofqudUjcWqNERY5ZCgdILdeiG3FHI1F-6V6hg&oe=659D6046",
        "Gosford": "https://cdn.revolutionise.com.au/logos/4nymemn5sfvawrqu.png",
        "Crusaders": "https://cdn.revolutionise.com.au/logos/p4ktpeyrau8auvro.png",
        "Colts": "https://cdn.revolutionise.com.au/logos/nuopppokzejl0im6.png",
    }

    with st.expander("Show full results table", expanded=False):
        _results = game_results.drop(columns=["team", "grade", "finals"])
        st.dataframe(_results, hide_index=True, use_container_width=True)

    content = (
        lambda round, location, field, image1_url, team1, text1, image2_url, text2, team2: f"""
        <div style="text-align: center; line-height: 1.0;">
            <p style="font-size: 18px;"><strong>Round { round }</strong></p>
        </div>
        <div style="text-align: center; line-height: 1.0;">
            <p style="font-size: 18px;"><strong>{ location } - { field } field</strong></p>
        </div>
        <div style="display: flex; justify-content: space-around; align-items: center; line-height: 1.0;">
            <div style="text-align: center;">
                <img src="{ image1_url }" alt="West Team" width="100">
                <p></p>
                <p>{ team1 }</p>
            </div>
            <div style="text-align: center;">
                <p><strong><span style="font-size: 36px;">{ text1 }</strong></p>
            </div>
            <div style="text-align: center;">
                <p><strong><span style="font-size: 36px;"> - </strong></p>
            </div>
            <div style="text-align: center;">
                <p><strong><span style="font-size: 36px;">{ text2 }</strong></p>
            </div>
            <div style="text-align: center;">
                <img src="{ image2_url }" alt="Opposition" width="100">
                <p></p>
                <p>{ team2 }</p>
            </div>
        </div>
        """
    )
    for _, row in game_results.iterrows():
        if row["opposition"] == "BYE":
            continue
        with st.container(border=True):
            st.markdown(
                content(
                    row["round"],
                    row["location_name"],
                    row["field"],
                    assets.get(row["team"]),
                    row["team"],
                    int(float(row["goals_for"])),
                    assets.get(row["opposition"]),
                    int(float(row["goals_against"])),
                    row["opposition"],
                ),
                unsafe_allow_html=True,
            )
            st.write("")


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
