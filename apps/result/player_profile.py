from dataclasses import dataclass
import streamlit as st

from config import config
from utils import select_box_query
from result.models import player_data, player_names


@dataclass
class Player:
    name: str
    grade: str
    games_played: int
    games_won: int
    goals: int
    green_cards: int
    yellow_cards: int
    red_cards: int

    @property
    def total_cards(self) -> int:
        return self.green_cards + self.yellow_cards + self.red_cards

    @property
    def goals_per_game(self) -> float:
        if self.goals == 0 or self.games_played == 0:
            return 0.0
        return self.goals / self.games_played

    @property
    def percent_games_won(self) -> str:
        return f"{(self.games_won / self.games_played) * 100:.1f}%"


def main() -> None:
    """Display player results"""

    # Display the filters
    col1, col2, _, _ = st.columns(
        [2, 2, 2, 2], gap="small", vertical_alignment="center"
    )
    season = select_box_query(
        "Season",
        config.app.seasons,
        col1,
        "Select season...",
    )
    if not season:
        # Seasons are stored in ascending order
        season = config.app.seasons[::-1][0]

    players = player_names(season)
    player_name = select_box_query(
        "Player",
        players["player"].values.tolist(),
        col2,
        "Select player...",
    )
    if not player_name:
        # By default display player with the most goals
        player_name = players["player"].values.tolist()[0]
    player_id = players[players["player"] == player_name]["id"].values[0]
    st.subheader("", divider="green")

    # Load player data
    df = player_data(player_id, season)
    if not df.shape[0]:
        st.warning(f"No games found for {player_name} in the {season} season")
        return

    player = Player(
        name=player_name,
        grade=df["player_graded"].unique()[0],
        games_played=int(df.shape[0]),
        games_won=df[df["result"] == "win"].shape[0],
        goals=int(df["goals"].sum()),
        green_cards=int(df["green_card"].sum()),
        yellow_cards=int(df["yellow_card"].sum()),
        red_cards=int(df["red_card"].sum()),
    )

    if not player.games_played:
        st.warning(f"{ player_name } hasn't played any games in the { season } season.")
        return

    display_html_header(player.name, season, player.grade)

    # Display the metrics
    col1, col2, col3, col4, col5 = st.columns(
        [1, 1, 1, 1, 1], gap="small", vertical_alignment="center"
    )
    col1.metric("Games played", player.games_played)
    col2.metric("Games won %", player.percent_games_won)
    col3.metric("Goals", player.goals)
    col4.metric("Goals per game", player.goals_per_game)
    col5.metric("Cards", player.total_cards)

    # Display the games played
    st.subheader("Games played")
    player_table = df[
        [
            "team",
            "grade",
            "round",
            "location_name",
            "opposition",
            "goals",
            "cards",
            "goals_for",
            "goals_against",
            "result",
        ]
    ].rename(
        columns={
            "team": "Team",
            "grade": "Grade",
            "round": "Round",
            "location_name": "Location",
            "opposition": "Opposition",
            "goals": "Individual Goals",
            "cards": "Individual Cards",
            "goals_for": "Team Goals For",
            "goals_against": "Team Goals Against",
            "result": "Result",
        }
    )
    st.dataframe(player_table, hide_index=True, use_container_width=True)


def display_html_header(player_name: str, season: str, grade: str):
    st.html(
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
            <h1>{player_name}</h1>
            <p>{season} Season : Player Graded: {grade}</p>
        </div>
        """
    )


main()
