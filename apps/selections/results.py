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
from selections.models import last_game_date, game_data, player_data


@auth_validation
def main(database_lock: bool = False, season: str = "2024") -> None:
    """Record game and players results.

    Args:
        database_lock (bool): True if the database lock is enabled.
        season (str): The hockey season, usually the calendar year.

    Retuns: None
    """
    st.title("Results")
    st.subheader("- Mark off players who played (regardless if they were selected)")
    st.subheader("- Add the results, and cards given", divider="green")

    # Date end filter
    max_date = last_game_date(season)
    col1, _, _ = st.columns(3)
    date_filter = col1.date_input(
        "Games for Week Ending",
        format="DD/MM/YYYY",
        value=max_date,
        min_value=dt.date(year=int(season), month=1, day=1),
        max_value=dt.date(year=int(season), month=12, day=31),
    )
    if not date_filter:
        st.error(f"Enter date to find games.")
        return

    ### load game data ###
    game_result = game_data(season, date_filter)
    if not game_result.shape[0]:
        return

    ### create input table for game results ###
    updated_game_results = input_game_results(game_result)
    # update game results in db
    game_changes = compare_dataframes(game_result, updated_game_results, "game_id")
    if game_changes.shape[0]:
        update_game_results(game_changes, database_lock)
        game_result = game_data(season, date_filter)

    ### Filters for player data ###
    col1, col2, _, _ = st.columns(4)
    team_round = col1.selectbox("Round", game_result["round"].unique().tolist())
    team = col2.selectbox("Team", game_result["team_name"].unique().tolist())

    ### Validation for player data ###
    if not season and not team_round:
        raise ValueError("Enter values for season and round.")

    ### Load player data ###
    player_result = player_data(season, team_round, team)
    if not player_result.shape[0]:
        st.error(
            """
                No games to selected player for.
                If there are games on this round contact the administrator.
            """
        )
        return

    st.subheader(
        f"""
            Record player results for round { team_round }\n
            { team } vs { player_result["opposition"].loc[0] }
        """
    )
    ### create input table for game results ###
    updated_player_results = input_player_results(player_result)
    # update game results in db
    # TODO: Fully implement this
    changes = compare_dataframes(player_result, updated_player_results, "selection_id")
    if not changes.shape[0]:
        return

    # update rows
    selection_updates = changes[changes["create_selections"] == False]
    st.write("Update selections data", selection_updates)
    update_player_selections(
        selection_updates,
        database_lock,
    )
    result_updates = changes[changes["create_results"] == False]
    results_orig = player_result[
        ["selection_id", "goals", "green_card", "yellow_card", "red_card"]
    ].rename(
        columns={
            "goals": "orig_goals",
            "green_card": "orig_green",
            "yellow_card": "orig_yellow",
            "red_card": "orig_red",
        }
    )
    result_updates = result_updates.merge(results_orig, on="selection_id", how="inner")
    result_updates.loc[:, "result_change"] = result_updates[
        [
            "goals",
            "green_card",
            "yellow_card",
            "red_card",
            "orig_goals",
            "orig_green",
            "orig_yellow",
            "orig_red",
        ]
    ].sum(axis=1)
    result_updates = result_updates[
        (result_updates["result_change"] != 0)
        & (-result_updates["result_change"].isna())
    ]
    st.write("Update results data", result_updates)
    update_player_results(
        result_updates,
        database_lock,
    )

    # create rows
    create_selections = changes[changes["create_selections"] == True]
    st.write("Create selections data", create_selections)
    create_player_selections(
        create_selections,
        database_lock,
    )
    create_results = changes[changes["create_results"] == True]
    create_results.loc[:, "result_change"] = create_results[
        ["goals", "green_card", "yellow_card", "red_card"]
    ].sum(axis=1)
    create_results = create_results[
        (create_results["result_change"] != 0)
        & (-create_results["result_change"].isna())
    ]
    st.write("Create results data", create_results)
    create_player_results(create_results, lock=database_lock)

    # refresh data
    player_result = player_data(season, team_round, team)


def input_game_results(df: pd.DataFrame) -> pd.DataFrame:
    """Update the game results.

    Args:
        df (pd.DataFrame): The dataframe to be updated.

    Returns:
        pd.DataFrame: The updated dataframe.
    """
    # TODO: add schema validation on df
    game_id = df["game_id"]
    _df = df.drop(columns=["game_id"])
    with st.form("Game results"):
        result = st.data_editor(
            _df,
            column_config={
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
            disabled=[
                "team_name",
                "opposition",
                "round",
                "game_time",
                "selected",
                "played",
            ],
            use_container_width=True,
            hide_index=True,
        )
        result.loc[:, "game_id"] = game_id
        commit_changes = st.form_submit_button("Submit")
    # Only update data when the user hits submit, otherwise return the same dataframe
    if not commit_changes:
        return df
    return result[df.columns].fillna({"goals_for": 0, "goals_against": 0})


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
        update_data("games", "goals_for", row["game_id"], row["goals_for"])
        update_data("games", "goals_against", row["game_id"], row["goals_against"])


def input_player_results(df: pd.DataFrame):
    """Update the player results.

    Args:
        df (pd.DataFrame): The dataframe to be updated.

    Returns:
        pd.DataFrame: The updated dataframe.
    """
    player_id = df["player_id"]
    game_id = df["game_id"]
    selection_id = df["selection_id"]
    create_results = df["create_results"]
    create_selections = df["create_selections"]
    _df = df.drop(
        columns=[
            "player_id",
            "game_id",
            "selection_id",
            "create_results",
            "create_selections",
        ]
    )
    with st.form("Player results"):
        result = st.data_editor(
            _df,
            column_config={
                "goal_keeper": st.column_config.CheckboxColumn(
                    "Goal Keeper",
                    help="Goal keeper selected to play.",
                    default=False,
                ),
                "played": st.column_config.CheckboxColumn(
                    "Played",
                    help="Player played the game.",
                    default=False,
                ),
                "goals": st.column_config.NumberColumn(
                    "Goals",
                    help="Goals the player scored.",
                    default=0,
                ),
                "green_cards": st.column_config.NumberColumn(
                    "Green Cards",
                    help="Green cards given to the player.",
                    default=0,
                ),
                "yellow_cards": st.column_config.NumberColumn(
                    "Yellow Cards",
                    help="Yellow cards given to the player.",
                    default=0,
                ),
                "red_cards": st.column_config.NumberColumn(
                    "Red Cards",
                    help="Red cards given to the player.",
                    default=0,
                ),
            },
            disabled=[
                "opposition",
                "players_name",
                "players_grade",
                "selected",
            ],
            use_container_width=True,
            hide_index=True,
        )
        result.loc[:, "player_id"] = player_id
        result.loc[:, "game_id"] = game_id
        result.loc[:, "selection_id"] = selection_id
        result.loc[:, "create_results"] = create_results
        result.loc[:, "create_selections"] = create_selections
        result.loc[
            (result["goals"] > 0)
            | (result["green_card"] > 0)
            | (result["yellow_card"] > 0)
            | (result["red_card"] > 0),
            "played",
        ] = True
        commit_changes = st.form_submit_button("Submit")

    # Only update data when the user hits submit
    if not commit_changes:
        return df
    return result[df.columns]


def update_player_results(df: pd.DataFrame, lock: bool = True) -> None:
    """Write the player updates to the database.

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
        update_data("results", "goals", row["selection_id"], row["goals"])
        update_data("results", "red_card", row["selection_id"], row["red_card"])
        update_data("results", "yellow_card", row["selection_id"], row["yellow_card"])
        update_data("results", "green_card", row["selection_id"], row["green_card"])


def update_player_selections(df: pd.DataFrame, lock: bool = True) -> None:
    """Write the player updates to the database.

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
        update_data("selections", "played", row["selection_id"], row["played"])
        update_data(
            "selections", "goal_keeper", row["selection_id"], row["goal_keeper"]
        )


def create_player_results(df: pd.DataFrame, lock: bool = True) -> None:
    """Create the player results in the database.

    Args:
        df (pd.DataFrame): The dataframe of rows to be created.
        lock (bool, optional): True if the database lock is enabled. Defaults to True.

    Returns: None
    """
    # TODO: Add validation
    if lock:
        st.error("Database is locked, contact the administrator.")
        return
    for _, row in df.iterrows():
        create_data(
            "results",
            (
                "id",
                "create_ts",
                "update_ts",
                "goals",
                "red_card",
                "yellow_card",
                "green_card",
            ),
            (
                row["selection_id"],
                str(add_timestamp()),
                str(add_timestamp()),
                row["goals"],
                row["red_card"],
                row["yellow_card"],
                row["green_card"],
            ),
        )


def create_player_selections(df: pd.DataFrame, lock: bool = True) -> None:
    """Create the player results in the database.

    Args:
        df (pd.DataFrame): The dataframe of rows to be created.
        lock (bool, optional): True if the database lock is enabled. Defaults to True.

    Returns: None
    """
    # TODO: Add validation
    if lock:
        st.error("Database is locked, contact the administrator.")
        return
    for _, row in df.iterrows():
        create_data(
            "selections",
            (
                "id",
                "create_ts",
                "update_ts",
                "game_id",
                "player_id",
                "goal_keeper",
                "selected",
                "played",
            ),
            (
                row["selection_id"],
                str(add_timestamp()),
                str(add_timestamp()),
                row["game_id"],
                row["player_id"],
                row["goal_keeper"],
                row["selected"],
                row["played"],
            ),
        )


main()
