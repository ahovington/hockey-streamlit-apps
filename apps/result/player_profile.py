from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
import pandas as pd
import streamlit as st

from config import config
from utils import select_box_query
from result.models import player_data, player_names


class Result(Enum):
    WIN = auto()
    DRAW = auto()
    LOSS = auto()


@dataclass
class Game:
    team: str
    grade: str
    round: str
    location: str
    opposition: str
    individual_goals: int
    individual_cards: int
    team_goals_for: int
    team_goals_against: int

    @property
    def result(self) -> Result:
        result = Result.WIN
        if self.team_goals_for == self.team_goals_against:
            result = Result.DRAW
        if self.team_goals_for < self.team_goals_against:
            result = Result.LOSS
        return result

    def to_dict(self):
        return {
            "Team": self.team,
            "Grade": self.grade,
            "Round": self.round,
            "Location": self.location,
            "Opposition": self.opposition,
            "Individual Goals": self.individual_goals,
            "Individual Cards": self.individual_cards,
            "Team Goals For": self.team_goals_for,
            "Team Goals Against": self.team_goals_against,
            "Result": self.result.name,
        }


@dataclass
class Player:
    name: str
    grade: str
    games_played: int
    goals: int
    green_cards: int
    yellow_cards: int
    red_cards: int
    games: list[Game]

    @property
    def games_won(self) -> int:
        return sum([1 for game in self.games if game.result == Result.WIN])

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
    season = select_box_query("Season", config.app.seasons, col1, "Select season...")
    season = season if season else config.app.seasons[0]

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

    player_results = load_player_results(player_id, season)

    if not player_results:
        st.warning(f"{ player_name } hasn't played any games in the { season } season.")
        return

    display_html_header(player_results.name, season, player_results.grade)

    display_metrics(player_results)

    display_games_table(player_results.games)


def load_player_results(player_id: str, season: str) -> Optional[Player]:
    players_games = player_data(player_id, season)
    if not players_games.shape[0]:
        st.warning(f"No games found for player in the {season} season")
        return
    games = []
    for _, game in players_games.iterrows():
        games += [
            Game(
                team=game["team"],
                grade=game["grade"],
                round=game["round"],
                location=game["location_name"],
                opposition=game["opposition"],
                individual_goals=int(game["goals"]),
                individual_cards=int(game["cards"]),
                team_goals_for=int(game["goals_for"]),
                team_goals_against=int(game["goals_against"]),
            )
        ]
    return Player(
        name=players_games["player"].unique()[0],
        grade=players_games["player_graded"].unique()[0],
        games_played=int(players_games.shape[0]),
        goals=int(players_games["goals"].sum()),
        green_cards=int(players_games["green_card"].sum()),
        yellow_cards=int(players_games["yellow_card"].sum()),
        red_cards=int(players_games["red_card"].sum()),
        games=games,
    )


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


def display_metrics(player: Player) -> None:
    col1, col2, col3, col4, col5 = st.columns(
        [1, 1, 1, 1, 1], gap="small", vertical_alignment="center"
    )
    col1.metric("Games played", player.games_played)
    col2.metric("Games won %", player.percent_games_won)
    col3.metric("Goals", player.goals)
    col4.metric("Goals per game", player.goals_per_game)
    col5.metric("Cards", player.total_cards)


def display_games_table(games: list[Game]) -> None:
    st.subheader("Games played")
    _results = pd.DataFrame.from_records([game.to_dict() for game in games])
    st.dataframe(_results, hide_index=True, use_container_width=True)


main()
