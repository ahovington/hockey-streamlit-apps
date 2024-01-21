import streamlit as st

from utils import config, read_data, select_box_query, clean_query_params


def PlayerResults() -> None:
    """Display player results"""
    clean_query_params(["Application", "page", "Player", "Season"])

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

    if not player_name:
        st.warning("Pick a player from dropdown.")
        return
    st.write("")
    st.write("")

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
            <p>Position: Forward</p>
            <p>Team: XYZ United</p>
            <p>Description: { player_name } is a talented forward playing for XYZ United. He has exceptional skills and contributes significantly to the team's success.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
