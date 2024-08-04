from dataclasses import dataclass
import streamlit as st

from config import config
from utils import select_box_query
from result.models import team_results_data


@dataclass
class Teams:
    name: str
    games_played: int
    wins: int
    losses: int
    draws: int
    goals_for: int
    goals_against: int

    @property
    def calculate_points(self) -> int:
        return self.wins * 2 + self.draws

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against

    @property
    def points_percentage(self) -> str:
        return f"{ self.calculate_points / (self.games * 2) :.1%}"


def main() -> None:
    """Display game results"""

    _, col2, _, _, _ = st.columns([3, 2, 2, 2, 1], gap="small")
    season = select_box_query("Season", config.app.seasons, col2, "Select season...")
    if not season:
        st.warning("Pick a season from dropdown.")
        return

    st.subheader(
        f"""Results for { season }""",
        divider="green",
    )

    team_results = team_results_data(season)
    if not team_results.shape[0]:
        st.warning(f"No results found for season { season }")
        return

    for _, row in team_results.iterrows():
        team = Teams(
            name=row["team_name"],
            games_played=int(row["games_played"]),
            wins=int(row["win"]),
            losses=row["loss"],
            draws=row["draw"],
            goals_for=row["goals_for"],
            goals_against=row["goals_against"],
        )
        with st.container(border=True):
            team_layout(
                team.name,
                team.games_played,
                team.wins,
                team.losses,
                team.draws,
                team.calculate_points,
            )
            with st.expander("More detail"):
                team_detail_layout(
                    team.goals_for,
                    team.goals_against,
                    team.goal_difference,
                    team.points_percentage,
                )

                st.warning("Not fully implemented")
                st.write("Top Goal Scorers")
                # Data for the table (replace with your actual data)
                data = [
                    {"Name": "John Doe", "Goals": 15},
                    {"Name": "Jane Smith", "Goals": 12},
                    # Add more rows as needed
                ]
                st.table(data)


def team_layout(
    team_name: str,
    games_played: int,
    wins: int,
    losses: int,
    draws: int,
    points: int,
    title_size: int = 16,
    metric_size: int = 32,
):
    return st.html(
        f"""
        <div style="text-align: center; line-height: 1.0;">
            <p style="font-size: 18px;"><strong>{team_name} Grade</strong></p>
        </div>
        <div style="display: flex; justify-content: space-around; align-items: center; line-height: 1.0;">
            <div style="text-align: center;">
                <p><span style="font-size: {title_size}px;">Games</p>
                <p><strong><span style="font-size: {metric_size}px;">{games_played}</strong></p>
            </div>
            <div style="text-align: center;">
                <p><span style="font-size: {title_size}px;">Wins</p>
                <p><strong><span style="font-size: {metric_size}px;">{wins}</strong></p>
            </div>
            <div style="text-align: center;">
                <p><span style="font-size: {title_size}px;">Losses</p>
                <p><strong><span style="font-size: {metric_size}px;">{losses}</strong></p>
            </div>
            <div style="text-align: center;">
                <p><span style="font-size: {title_size}px;">Draws</p>
                <p><strong><span style="font-size: {metric_size}px;">{draws}</strong></p>
            </div>
            <div style="text-align: center;">
                <p><span style="font-size: {title_size}px;">Points</p>
                <p><strong><span style="font-size: {metric_size}px;">{points}</strong></p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def team_detail_layout(
    goals_for: int,
    goals_againt: int,
    goal_difference: int,
    points_percentage: str,
    title_size=12,
    metric_size=24,
):
    return st.html(
        f"""
        <div style="display: flex; justify-content: space-around; align-items: center; line-height: 1.0;">
            <div style="text-align: center;">
                <p><span style="font-size: {title_size}px;">Goals for</p>
                <p><strong><span style="font-size: {metric_size}px;">{goals_for}</strong></p>
            </div>
            <div style="text-align: center;">
                <p><span style="font-size: {title_size}px;">Goals against</p>
                <p><strong><span style="font-size: {metric_size}px;">{goals_againt}</strong></p>
            </div>    
            <div style="text-align: center;">
                <p><span style="font-size: {title_size}px;">Goal difference</p>
                <p><strong><span style="font-size: {metric_size}px;">{goal_difference}</strong></p>
            </div>
            <div style="text-align: center;">
                <p><span style="font-size: {title_size}px;">Points percentage</p>
                <p><strong><span style="font-size: {metric_size}px;">{points_percentage}</strong></p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


main()
