import datetime as dt
import streamlit as st
import pandas as pd

from utils import add_timestamp, compare_dataframes, create_data, read_data, update_data


def Games(database_lock: bool, season: str) -> None:
    """Record game and players results.

    Args:
        database_lock (bool): True if the database lock is enabled.
        season (str): The hockey season, usually the calendar year.

    Retuns: None
    """
    st.title("Games")
    st.subheader("Update game data")

    all_game_result = game_data(season)
    all_game_result.loc[:, "start_ts"] = pd.to_datetime(
        all_game_result.loc[:, "start_ts"]
    )
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


def game_data(
    season: str, date_end: dt.datetime = None, date_inteval: int = 6
) -> pd.DataFrame:
    """Extact the game data for the week.

    Args:
        season (str): The hockey season, usually the calendar year.
        date_end (dt.datetime): The end timestamp.
        date_inteval (int, optional): How many days before the date_end to include. Defualts to 6.

    Retuns:
        pd.DataFrame: The results of the query.
    """
    filters = [f"g.season = '{ season }'"]
    if date_end:
        date_start = date_end - dt.timedelta(days=date_inteval)
        filters.append("and")
        filters.append(f"g.start_ts between '{ date_start }' and '{ date_end }'")
    df = read_data(
        f"""
        select
            g.create_ts,
            g.update_ts,
            g.id as game_id,
            t.team || ' - ' || t.grade as team_name,
            t.team_order,
            g.opposition,
            g.start_ts,
            g.round,
            case
                when round = 'SF1' then '30'
                when round = 'PF1' then '40'
                when round = 'GF1' then '30'
                else round
            end as round_order,
            g.goals_for,
            g.goals_against
        from games as g
        inner join teams as t
        on g.team_id = t.id
        where { ' '.join(filters) }
        """
    ).replace("", None)
    df.loc[:, "round_order"] = df.loc[:, "round_order"].astype(int)
    df = df.sort_values(["team_order", "round_order"])
    ### game validation ###
    if not df.dropna(subset=["game_id"]).shape[0]:
        st.error(f"No game found for week ending { date_end }")
        return pd.DataFrame()
    return df[
        [
            "create_ts",
            "update_ts",
            "game_id",
            "team_name",
            "opposition",
            "round",
            "start_ts",
            "goals_for",
            "goals_against",
        ]
    ]


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
