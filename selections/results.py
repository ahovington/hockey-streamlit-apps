import datetime as dt
import streamlit as st
import pandas as pd

from utils import add_timestamp, compare_dataframes, create_data, read_data, update_data


def Results(database_lock: bool, season: str) -> None:
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
    max_date = read_data(
        f"""
        select max(start_ts) as max_ts
        from games
        where
            season = '{ season }'
            and start_ts < '{ dt.datetime.now() }'
        """
    ).iloc[0, 0]
    col1, _, _ = st.columns(3)
    date_filter = col1.date_input(
        "Games for Week Ending",
        format="DD/MM/YYYY",
        value=max_date,
        min_value=dt.date(year=int(season), month=1, day=1),
        max_value=dt.date(year=int(season), month=12, day=31),
    )

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
    team_round = col1.selectbox("Round", game_result["round"].unique())
    team = col2.selectbox("Team", game_result["team_name"].unique())

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
    result_updates = changes[changes["create_result"] == False]
    st.write("Update data", result_updates)
    update_player_results(
        result_updates,
        database_lock,
    )

    # create rows
    creates = changes[changes["create_result"] == True]
    st.write("Create data", creates)
    create_player_results(creates, lock=database_lock)

    # refresh data
    player_result = player_data(season, team_round, team)


def game_data(
    season: str, date_end: dt.datetime, date_inteval: int = 6
) -> pd.DataFrame:
    """Extact the game data for the week.

    Args:
        season (str): The hockey season, usually the calendar year.
        date_end (dt.datetime): The end timestamp.
        date_inteval (int, optional): How many days before the date_end to include. Defualts to 6.

    Retuns:
        pd.DataFrame: The results of the query.
    """
    date_start = date_end - dt.timedelta(days=date_inteval)
    df = read_data(
        f"""
        select
            g.id as game_id,
            t.team || ' - ' || t.grade as team_name,
            g.opposition,
            g.start_ts,
            g.round,
            g.goals_for,
            g.goals_against
        from games as g
        inner join teams as t
        on g.team_id = t.id
        where
            g.season = '{ season }'
            and g.start_ts between '{ date_start }' and '{ date_end }'
        order by
            t.team_order
        """
    ).replace("", None)
    ### Format the game start time ###
    df.loc[:, "game_time"] = pd.to_datetime(df.loc[:, "start_ts"]).dt.strftime(
        "%a %d %B, %-I:%M %p"
    )
    ### game validation ###
    if not df.dropna(subset=["game_id"]).shape[0]:
        st.error(f"No game found for week ending { date_end }")
        return pd.DataFrame()
    return df[
        [
            "game_id",
            "team_name",
            "opposition",
            "round",
            "game_time",
            "goals_for",
            "goals_against",
        ]
    ]


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
            disabled=["team_name", "opposition", "round", "game_time"],
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


def player_data(season: str, team_round: str, team: str) -> pd.DataFrame:
    """Extact the player data for the team and round.

    Args:
        season (str): The hockey season, usually the calendar year.
        team_round (str): The teams round of the season.
        team (str): The team results are being updated for.

    Retuns:
        pd.DataFrame: The results of the query.
    """
    df = read_data(
        f"""
        with _games as (
            select
                g.id as game_id,
                t.id as team_id,
                t.team_order,
                t.team || ' - ' || t.grade as team_name,
                g.round,
                g.opposition,
                g.start_ts
            from games as g
            inner join teams as t
            on g.team_id = t.id
            where
                g.season = '{ season }'
                and g.round = '{ team_round }'
                and t.team || ' - ' || t.grade = '{ team }'
        ),

        _selections as (
            select
                s.id as selection_id,
                s.player_id,
                s.game_id,
                g.team_id,
                s.goal_keeper,
                s.selected,
                s.played
            from selections as s
            inner join _games as g
            on s.game_id = g.game_id
        ),

        _registered_players as (
            select
                g.game_id,
                p.id as player_id,
                p.full_name as players_name,
                r.grade as players_grade,
                g.team_order,
                g.team_name,
                g.round,
                g.opposition,
                g.start_ts
            from players as p
            inner join registrations as r
            on p.id = r.national_id
            cross join _games as g
        ),

        _played_games as (
            select
                coalesce(s.selection_id, g.game_id || g.player_id) as selection_id,
                g.game_id,
                g.player_id,
                case
                    when r.id is null then true
                    else false
                end as create_result,
                g.opposition,
                g.players_name,
                g.players_grade,
                coalesce(s.selected, False) as selected,
                coalesce(s.goal_keeper, False) as goal_keeper,
                coalesce(s.played, False) as played,
                coalesce(r.goals, 0) as goals,
                coalesce(r.green_card, 0)  as green_card,
                coalesce(r.yellow_card, 0)  as yellow_card,
                coalesce(r.red_card, 0)  as red_card
            from _registered_players as g
            left join _selections as s
            on
                s.game_id = g.game_id
                and s.player_id = g.player_id
            left join results as r
            on s.selection_id = r.id
        )

        select *
        from _played_games
        order by
            selected desc,
            goal_keeper desc,
            players_grade desc
        """
    )
    return df.astype(
        {
            "selected": bool,
            "goal_keeper": bool,
            "played": bool,
            "goals": int,
            "green_card": int,
            "yellow_card": int,
            "red_card": int,
        }
    )


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
    create_result = df["create_result"]
    _df = df.drop(columns=["player_id", "game_id", "selection_id", "create_result"])
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
        result.loc[:, "create_result"] = create_result
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
        update_data("selections", "played", row["selection_id"], row["played"])
        update_data(
            "selections", "goal_keeper", row["selection_id"], row["goal_keeper"]
        )
        update_data("results", "goals", row["selection_id"], row["goals"])
        update_data("results", "red_card", row["selection_id"], row["red_card"])
        update_data("results", "yellow_card", row["selection_id"], row["yellow_card"])
        update_data("results", "green_card", row["selection_id"], row["green_card"])


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
