import streamlit as st

from config import config
from utils import read_data, select_box_query, clean_query_params


def main() -> None:
    """Display player results"""
    # clean_query_params(["Application", "Page", "Player", "Season"])

    _, col2, col3, col4, _ = st.columns([3, 2, 2, 2, 1], gap="small")
    player_name = select_box_query(
        "Player",
        read_data("select full_name as player from players order by full_name")[
            "player"
        ].values.tolist(),
        col2,
        "Select player...",
    )
    season = select_box_query("Season", config.app.seasons, col3, "Select season...")

    if not player_name or not season:
        st.warning("Pick a player and season from the dropdowns.")
        return
    st.write("")
    st.write("")

    df = player_data(player_name, season)

    if not df.shape[0]:
        st.warning(f"{ player_name } hasn't played any games in the { season } season.")
        return

    grade = df["player_graded"].unique()[0]
    games_played = df["games_played"].sum()

    st.markdown(
        f"""
        <div class="profile">
            <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
            }}
            .profile {{
                max-width: 600px;
                margin: 0 auto;
                text-align: center;
            }}
            img {{
                max-width: 100%;
                height: auto;
                border-radius: 50%;
            }}
        </style>
            <img src= { "https://maxfieldhockey.com/wp-content/uploads/2019/02/PlayerProfileHeadshot_Default.jpg" } alt="Player Avatar">
            <h1>{ player_name }</h1>
            <p>Player Graded: { grade }</p>
            <p>Games played in { season }: { games_played }</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    player_table = df[["grade_played", "goal_keeper", "games_played"]]
    player_table.columns = [
        "Grade played",
        "Played in goals",
        "Games played",
    ]
    player_table.loc[:, "Goals"] = 0
    st.dataframe(player_table, hide_index=True, use_container_width=True)


def player_data(player_name: str, season: str):
    """The data for the player

    Args:
        player_name str: The name of the player.
        season str: The hockey season.
    """
    return read_data(
        f"""
            select
                p.id as player_id,
                p.full_name as player,
                g.season,
                r.grade as player_graded,
                t.grade as grade_played,
                s.goal_keeper,
                s.played,
                count(*) as games_played
            from players as p
            left join registrations as r
            on p.id = r.player_id
            left join selections as s
            on p.id = s.player_id
            left join games as g
            on s.game_id = g.id and
                r.season = g.season
            left join teams as t
            on g.team_id = t.id
            where
                s.played = true and
                p.full_name = '{ player_name }' and
                r.season = '{ season }' and
                g.season = '{ season }'
            group by
                p.id,
                p.full_name,
                g.season,
                r.grade,
                t.grade,
                s.goal_keeper,
                s.played
            order by
                p.id
    """
    )


main()
