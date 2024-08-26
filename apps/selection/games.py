from dataclasses import dataclass
import datetime as dt
import streamlit as st
import pandas as pd

from config import config
from utils import (
    auth_validation,
    select_box_query,
    add_timestamp,
    compare_dataframes,
    create_data,
    update_data,
)
from selection.file_loader import FileUploader
from selection.models import (
    game_data,
    team_data,
    team_id_data,
    location_name_data,
    location_id_data,
    field_name_data,
)

REQUIRED_COLUMNS = [
    "SEASON",
    "ROUND",
    "TEAM",
    "GRADE",
    "LOCATION",
    "FIELD",
    "OPPOSITION",
    "DATE",
    "START_TIME",
    "FINALS",
]

file_loader = FileUploader(REQUIRED_COLUMNS)


@dataclass
class EnterGame:
    season: str
    round: str
    grade: str
    location: str
    field: str
    date: dt.date
    start_time: dt.datetime
    team: str
    opposition: str
    finals: bool

    @property
    def id(self) -> str:
        return f"{self.season}{self.grade}{self.team}{self.round}"

    @property
    def team_id(self) -> str:
        id = team_id_data(self.season, self.team, self.grade)
        if id.shape[0] > 1:
            raise ValueError("Team id returned more than one result.")
        return id.iloc[0, 0]

    @property
    def location_id(self) -> str:
        id = location_id_data(self.location, self.field)
        if id.shape[0] > 1:
            raise ValueError("Location id returned more than one result.")
        return id.iloc[0, 0]

    @property
    def start_ts(self) -> str:
        return dt.datetime(
            self.date.year,
            self.date.month,
            self.date.day,
            self.start_time.hour,
            self.start_time.minute,
        ).strftime("%Y-%m-%d %H:%M:%S")


@auth_validation
def main(database_lock: bool = False, season: str = "2024") -> None:
    """Record game and players results.

    Args:
        database_lock (bool): True if the database lock is enabled.
        season (str): The hockey season, usually the calendar year.

    Retuns: None
    """
    st.title("Games")
    col1, col2, col3, _ = st.columns(
        [2, 2, 2, 2], gap="small", vertical_alignment="center"
    )
    season = select_box_query("Season", config.app.seasons, col1, "Select season...")
    season = season if season else config.app.seasons[0]
    game_round = col2.text_input("Select Round")
    game_date = col3.date_input("Enter round date")
    st.write(f"{season=}, {game_round=}, {game_date=}")

    col1, col2, _, _ = st.columns(
        [2, 2, 2, 2], gap="small", vertical_alignment="center"
    )

    game_data_csv = file_loader.upload_file()
    # if game_data_csv is not None:
    #     col_mapping_input = map_upload_game_data_schema(
    #         game_data_csv.sample(1, random_state=42)
    #     )
    #     if col_mapping_input is not None:
    #         col_mapping_output = transform_mapping_input(col_mapping_input)
    #         if not validate_required_columns(col_mapping_output):
    #             return
    #         st.write(col_mapping_output)

    #         st.write("Mapping data")

    #         game_data_input = game_data_csv[list(col_mapping_output.keys())].rename(
    #             columns=col_mapping_output
    #         )
    #         st.dataframe(game_data_input)

    st.write("Or enter game data.")
    game_data = format_game_data(
        season,
        game_round,
        game_input_form(create_game_data(season, game_date)),
    )

    # if st.button("Write data to DB"):
    #     for game in game_data:
    #         write_game_data(
    #             game.id,
    #             game.season,
    #             game.team_id,
    #             game.location_id,
    #             game.round,
    #             game.finals,
    #             game.opposition,
    #             game.start_ts,
    #             database_lock,
    #         )

    # with st.expander("Update game data", expanded=False):
    #     update_game_data(database_lock, season)


def create_game_data(season: str, game_date: dt.date) -> pd.DataFrame:
    """Collect game data.

    Args:
        season (str): The season the game is part of.

    Returns:
        pd.DataFrame: A dataframe of the games this round.
    """
    games = []
    for _, row in team_data(season).iterrows():
        games += [
            {
                "TEAM": row["team"],
                "GRADE": row["grade"],
                "LOCATION": "Newcastle International Hockey Centre",
                "FIELD": None,
                "OPPOSITION": None,
                "DATE": game_date,
                "START_TIME": None,
                "FINALS": False,
            }
        ]
    return pd.DataFrame(games)


def game_input_form(game_data: pd.DataFrame) -> pd.DataFrame:
    entered_games_df = st.data_editor(
        game_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "LOCATION": st.column_config.SelectboxColumn(
                "Select Location", options=location_name_data().iloc[:, 0]
            ),
            "FIELD": st.column_config.SelectboxColumn(
                "Select Field", options=field_name_data().iloc[:, 0]
            ),
            "OPPOSITION": st.column_config.TextColumn(),
            "DATE": st.column_config.DateColumn(),
            "START_TIME": st.column_config.TimeColumn(),
        },
    )
    return entered_games_df


def format_game_data(
    season: str, round: str, game_data: pd.DataFrame
) -> list[EnterGame]:
    entered_games = []
    for _, row in game_data.iterrows():
        entered_games += [
            EnterGame(
                season=season,
                round=round,
                team=row["TEAM"],
                grade=row["GRADE"],
                location=row["LOCATION"],
                field=row["FIELD"],
                opposition=row["OPPOSITION"],
                date=row["DATE"],
                start_time=row["START_TIME"],
                finals=row["FINALS"],
            )
        ]
    return entered_games


def update_game_data(database_lock: bool, season: str):
    """Update data of games already created.

    Args:
        database_lock (bool): True if the database lock is enabled.
        season (str): The hockey season, usually the calendar year.

    Retuns: None
    """

    all_game_result = game_data(season)
    if not all_game_result.shape[0]:
        return
    updated_all_game_results = input_all_game_results(all_game_result)
    all_game_changes = compare_dataframes(
        all_game_result, updated_all_game_results, "game_id"
    )
    st.table(all_game_changes)
    if all_game_changes.shape[0]:
        update_game_results(all_game_changes, database_lock)


def input_all_game_results(df: pd.DataFrame) -> pd.DataFrame:
    """Update the game results.

    Args:
        df (pd.DataFrame): The dataframe to be updated.
        table_name (str): Unique name of the input table.

    Returns:
        pd.DataFrame: The updated dataframe.
    """
    # TODO: add schema validation on df
    game_id = df["game_id"]
    _df = df.drop(columns=["game_id"])
    with st.form("Results for all games"):
        result = st.data_editor(
            _df,
            column_config={
                "start_ts": st.column_config.DatetimeColumn(
                    "Start time",
                    help="Start time of the game.",
                ),
                "goals_for": st.column_config.NumberColumn(
                    "Goals for",
                    help="Goals scored for.",
                    default=0,
                ),
                "goals_against": st.column_config.NumberColumn(
                    "Goals against",
                    help="Goals scored against.",
                    default=0,
                ),
            },
            use_container_width=True,
            hide_index=True,
        )
        result.loc[:, "game_id"] = game_id
        commit_changes = st.form_submit_button("Submit")
    # Only update data when the user hits submit, otherwise return the same dataframe
    if not commit_changes:
        return df
    return result[df.columns].fillna({"goals_for": 0, "goals_against": 0})


def write_game_data(
    id: str,
    season: str,
    team_id: str,
    location_id: str,
    round: str,
    finals: bool,
    opposition: str,
    start_ts: str,
    lock: bool = True,
) -> None:
    if lock:
        st.error("Database is locked, contact the administrator.")
        return
    create_data(
        "games",
        (
            "id",
            "create_ts",
            "update_ts",
            "season",
            "team_id",
            "location_id",
            "round",
            "finals",
            "opposition",
            "start_ts",
        ),
        (
            id,
            str(add_timestamp()),
            str(add_timestamp()),
            season,
            team_id,
            location_id,
            round,
            finals,
            opposition,
            start_ts,
        ),
    )


def update_game_results(df: pd.DataFrame, lock: bool = True) -> None:
    """Write the game updates to the database.

    Args:
        df (pd.DataFrame): The dataframe of updates to be made.
        lock (bool, optional): True if the database lock is enabled. Defaults to True.

    Returns: None
    """
    # TODO: Add validation
    if lock:
        st.error("Database is locked, contact the administrator.")
        return
    for _, row in df.iterrows():
        update_data(
            "games",
            "start_ts",
            row["game_id"],
            row["start_ts"],
            value_string_type=True,
            verbose=True,
        )
        update_data("games", "goals_for", row["game_id"], row["goals_for"])
        update_data("games", "goals_against", row["game_id"], row["goals_against"])


main()
