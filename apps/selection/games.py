import datetime as dt
import streamlit as st
import pandas as pd

from utils import (
    auth_validation,
    add_timestamp,
    compare_dataframes,
    create_data,
    update_data,
)
from selection.models import (
    game_data,
    team_name_data,
    team_id_data,
    grade_name_data,
    location_name_data,
    location_id_data,
    field_name_data,
)


@auth_validation
def main(database_lock: bool = False, season: str = "2024") -> None:
    """Record game and players results.

    Args:
        database_lock (bool): True if the database lock is enabled.
        season (str): The hockey season, usually the calendar year.

    Retuns: None
    """
    st.title("Games")
    with st.expander("Enter game data", expanded=False):
        id, team_id, location_id, round, finals, opposition, start_ts = enter_game_data(
            season
        )
        if st.button("Submit"):
            write_game_data(
                id,
                season,
                team_id,
                location_id,
                round,
                finals,
                opposition,
                start_ts,
                database_lock,
            )

    with st.expander("Update game data", expanded=False):
        update_game_data(database_lock, season)


def enter_game_data(season: str):
    # Enter data
    team = st.selectbox("Team", team_name_data(season))
    grade = st.selectbox("Grade", grade_name_data(season))
    location = st.selectbox("Location", location_name_data())
    field = st.selectbox("Field", field_name_data())
    round = st.text_input("Round")
    opposition = st.text_input("Opposition")
    date = st.date_input("Game date")
    start_time = st.time_input("Start time")
    finals = st.selectbox("Finals", [False, True])

    # Transform inputs
    id = f"{season}{grade}{team}{round}"
    team_id = team_id_data(season, team, grade)
    location_id = location_id_data(location, field)
    start_ts = dt.datetime(
        date.year, date.month, date.day, start_time.hour, start_time.minute
    ).strftime("%Y-%m-%d %H:%M:%S")
    return id, team_id, location_id, round, finals, opposition, start_ts


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
        all_game_result = game_data(season)


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
