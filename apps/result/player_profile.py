import streamlit as st

from config import config
from utils import select_box_query
from result.models import player_data, player_names


def main() -> None:
    """Display player results"""

    _, col2, col3, col4, _ = st.columns([3, 2, 2, 2, 1], gap="small")
    player_name = select_box_query(
        "Player",
        player_names()["player"].values.tolist(),
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


main()
