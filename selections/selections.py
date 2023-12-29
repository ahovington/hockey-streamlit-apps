import datetime as dt
import streamlit as st
import numpy as np
import pandas as pd

from utils import (
    add_timestamp,
    calculate_date_interval,
    compare_dataframes,
    create_data,
    read_data,
    update_data,
)


def Selections(database_lock: bool, season: str):
    st.title("Selections")
    st.subheader("Select players to play", divider="green")

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

    start_date_ui, end_date_ui = calculate_date_interval(date_filter, filter=False)
    st.write(f"""Games between { start_date_ui } and { end_date_ui } """)

    ### Generate selections table ###
    with st.expander(f"Preview selections", expanded=False):
        col1, _, _ = st.columns(3)
        if col1.button(f"Generate selections", use_container_width=True):
            pass

        selected = selections_output_data(season, date_filter)
        if selected.shape[0]:
            output_selections_table(
                selected,
                [
                    "round",
                    "opposition",
                    "game_time",
                    "location",
                    "field",
                    "manager",
                    "manager_mobile",
                ],
                end_date_ui,
            )

    ### load game data and show games on this week ###
    game = game_data(season, date_filter)
    if not game.shape[0]:
        return

    st.dataframe(
        game[["round", "team_name", "opposition", "game_time", "players_selected"]],
        use_container_width=True,
        hide_index=True,
    )

    ### Filters for player data ###
    col1, col2, _, _ = st.columns(4)
    round = col1.selectbox("Round", game["round"].unique())
    team = col2.selectbox("Team", game["team_name"].unique())

    ### Validation for player data ###
    if not season and not round:
        raise ValueError("Enter values for season and round.")

    ### Load player data and show the selections table ###
    selections = selections_input_data(season, round, team)
    if not selections.shape[0]:
        return

    # return updated table and identify changes
    updated_selections = input_selections_table(selections, team)
    changes = compare_dataframes(selections, updated_selections, "player_id")

    if not changes.shape[0]:
        return

    # update rows
    updates = changes[changes["create_selection"] == False]
    st.write("Update data", updates)
    update_selection(updates, lock=database_lock)

    # create rows
    creates = changes[changes["create_selection"] == True]
    st.write("Create data", creates)
    create_selection(creates, lock=database_lock)

    # refresh data
    game = game_data(season, date_filter)
    selections = selections_input_data(season, round, team)


def selections_output_data(
    season: str, date_end: dt.datetime, date_inteval: int = 6
) -> pd.DataFrame:
    date_start, date_end = calculate_date_interval(date_end, date_inteval)
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
                g.start_ts,
                t.manager,
                t.manager_mobile,
                l.name as location,
                l.field
            from games as g
            inner join teams as t
            on g.team_id = t.id
            left join locations as l
            on g.location_id = l.id
            where
                g.season = '{ season }'
                and g.start_ts between '{ date_start }' and '{ date_end }'
        ),

        _selections as (
            select
                s.id as selection_id,
                g.team_name,
                p.full_name as players_name,
                s.goal_keeper,
                g.round,
                g.opposition,
                g.start_ts,
                g.team_order,
                g.manager,
                g.manager_mobile,
                g.location,
                g.field
            from _games as g
            left join selections as s
            on s.game_id = g.game_id
            left join players as p
            on s.player_id = p.id
            where s.selected = True
        )

        select *
        from _selections
        order by team_order
        """
    )
    ### validation ###
    if not df.shape[0]:
        st.error(
            "There are no selections for this date range. If there are games showing, ensure players have been selected for those games."
        )
        return pd.DataFrame()
    df.loc[:, "game_time"] = pd.to_datetime(df.loc[:, "start_ts"]).dt.strftime(
        "%a %d %B, %-I:%M %p"
    )
    return df


def output_selections_table(
    df: pd.DataFrame, header_fields: str, week_end: str
) -> None:
    # Calculate output table column order
    col_order = (
        df[["team_name", "team_order"]]
        .drop_duplicates()
        .sort_values("team_order")["team_name"]
        .values
    )

    ### Split the df into goalies and field players ###
    # Goalies
    _selected_keeper = df[df["goal_keeper"] == True].sort_values("team_order")
    _selected_keeper.loc[:, "id"] = (
        _selected_keeper["team_name"] + _selected_keeper["round"]
    )
    selected_keeper = _selected_keeper.drop_duplicates(subset=["team_name", "round"])
    dup_keeper = compare_dataframes(_selected_keeper, selected_keeper, "id")
    if dup_keeper.shape[0]:
        for i, row in dup_keeper.iterrows():
            st.error(
                f"""
                Multiple Goal Keepers have been chosen for team { row["team_name"] } and round { row["round"] }\n
                The selections only support one Goal keeper, **{ row["players_name"].upper() }** has been removed from this game.\n
                To fix this only select one keeper in the selections.
                """
            )
    selected_keeper.loc[:, "selection_no"] = "GK"
    # Field player
    selected_player = df[df["goal_keeper"] == False].sort_values("team_order")
    selected_player.loc[:, "selection_no"] = (
        selected_player.sort_values(
            ["goal_keeper", "players_name"], ascending=[False, True]
        )
        .groupby(["team_name", "round"])
        .cumcount()
    ) + 1

    ### Create header ###
    game_details = (
        df[["team_name"] + header_fields]
        .drop_duplicates()
        .set_index(["team_name", "round"])
        .T.fillna("")
    )

    # Pivot the dataframe
    pivot_selections = pd.concat(
        [
            game_details,
            pd.DataFrame({col: [""] for col in game_details.columns}, index=[""]),
            selected_keeper.pivot(
                columns=["team_name", "round"],
                values="players_name",
                index="selection_no",
            ),
            selected_player.pivot(
                columns=["team_name", "round"],
                values="players_name",
                index="selection_no",
            ),
        ]
    )[col_order].fillna("")

    def highlight_players_multiple_games(x, color):
        # Highlight players that play twice
        dup_players = df[df["players_name"].duplicated()]["players_name"].values
        return np.where(x in dup_players, f"background-color: {color};", None)

    col1, col2 = st.columns([3, 10])
    col1.image("./rosella.png")
    col2.title(f"West Hockey Selections, for the week ending { week_end }")
    st.dataframe(
        pivot_selections.style.applymap(
            highlight_players_multiple_games,
            color="yellow",
            subset=(slice("GK", np.max(selected_player["selection_no"]))),
        ),
        use_container_width=True,
        height=740,
    )


def game_data(season: str, date_end: dt.datetime, date_inteval: int = 6):
    date_start, date_end = calculate_date_interval(date_end, date_inteval)
    df = read_data(
        f"""
        with count_selections as (
            select
                game_id,
                count(*) as players_selected
            from selections
            where selected = true
            group by
                game_id
        )

        select
            g.id,
            t.grade,
            t.team,
            t.team || ' - ' || t.grade as team_name,
            g.opposition,
            g.start_ts,
            g.round,
            cs.players_selected
        from games as g
        inner join teams as t
        on g.team_id = t.id
        left join count_selections as cs
        on g.id = cs.game_id
        where
            g.season = '{ season }'
            and g.start_ts between '{ date_start }' and '{ date_end }'
        """
    ).replace("", None)
    ### game validation ###
    if not df.shape[0]:
        st.error(f"No game found for week ending { date_end }")
        return pd.DataFrame()
    df.loc[:, "game_time"] = pd.to_datetime(df.loc[:, "start_ts"]).dt.strftime(
        "%a %d %B, %-I:%M %p"
    )
    return df[["round", "team_name", "opposition", "game_time", "players_selected"]]


def selections_input_data(season: str, round: str, team: str):
    df = read_data(
        f"""
        with _games as (
            select
                g.id as game_id,
                t.id as team_id
            from games as g
            inner join teams as t
            on g.team_id = t.id
            where
                g.season = '{ season }'
                and g.round = '{ round }'
                and t.team || ' - ' || t.grade = '{ team }'
        ),
        
        _selections as (
            select
                s.id as selection_id,
                s.player_id,
                s.game_id,
                g.team_id,
                s.goal_keeper,
                s.selected
            from selections as s
            inner join _games as g
            on s.game_id = g.game_id
        ),

        _registered_players as (
            select
                p.id as player_id,
                p.full_name as players_name,
                g.game_id,
                r.team as players_main_team,
                r.grade as players_grade
            from players as p
            inner join registrations as r
            on p.id = r.national_id
            cross join _games as g
        )

        select
            coalesce(s.selection_id, rp.game_id || rp.player_id) as selection_id,
            case
                when s.selection_id is null then true
                else false
            end create_selection,
            rp.game_id,
            rp.player_id,
            rp.players_name,
            rp.players_main_team,
            rp.players_grade,
            coalesce(s.selected, false) as selected,
            coalesce(s.goal_keeper, false) as goal_keeper
        from _registered_players as rp
        left join _selections as s
        on
            rp.player_id = s.player_id
            and rp.game_id = s.game_id
        order by
            s.selected desc,
            s.goal_keeper desc
        """
    )
    if not df.shape[0]:
        st.error(
            f"No games to selected player for. If there are games on this round contact the administrator."
        )
        return pd.DataFrame()
    return df


def input_selections_table(
    df: pd.DataFrame,
    team: str,
):
    ordered_df = df.sort_values(
        ["goal_keeper", "selected", "players_main_team"],
        ascending=[False, False, False],
    ).copy()
    if not ordered_df["selected"].sum():
        ordered_df = pd.concat(
            [
                ordered_df[ordered_df["players_main_team"] == team],
                ordered_df[ordered_df["players_main_team"] != team].sort_values(
                    "players_main_team"
                ),
            ]
        )
    # remove id columns
    selection_id = ordered_df["selection_id"]
    game_id = ordered_df["game_id"]
    player_id = ordered_df["player_id"]
    create_selection = ordered_df["create_selection"]
    players_main_team = ordered_df["players_main_team"]
    ordered_df = ordered_df.drop(
        columns=[
            "selection_id",
            "game_id",
            "player_id",
            "players_main_team",
            "create_selection",
        ]
    )
    with st.form("Selections"):
        result = st.data_editor(
            ordered_df,
            column_config={
                "selected": st.column_config.CheckboxColumn(
                    "Selected",
                    help="Player selected to play.",
                    default=False,
                ),
                "goal_keeper": st.column_config.CheckboxColumn(
                    "Goal Keeper",
                    help="Goal keeper selected to play.",
                    default=False,
                ),
            },
            disabled=["selection_id", "players_name", "players_grade"],
            use_container_width=True,
            hide_index=True,
        )
        # Force selected to be true if goal_keeper is true
        result.loc[result["goal_keeper"] == True, "selected"] = True
        # add id columns back
        result.loc[:, "selection_id"] = selection_id
        result.loc[:, "game_id"] = game_id
        result.loc[:, "player_id"] = player_id
        result.loc[:, "create_selection"] = create_selection
        result.loc[:, "players_main_team"] = players_main_team
        commit_changes = st.form_submit_button("Submit")
    # Only update data when the user hits submit
    if not commit_changes:
        return df
    return result[df.columns]


def update_selection(selections: pd.DataFrame, lock: bool = True) -> None:
    # TODO: Add validation
    if lock:
        st.error("Database is locked, contact the administrator.")
        return
    for _, row in selections.iterrows():
        update_data(
            "selections", "goal_keeper", row["selection_id"], row["goal_keeper"]
        )
        update_data("selections", "selected", row["selection_id"], row["selected"])


def create_selection(selections: pd.DataFrame, lock: bool = True) -> None:
    # TODO: Add validation
    if lock:
        st.error("Database is locked, contact the administrator.")
        return
    for _, row in selections.iterrows():
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
            ),
            (
                row["selection_id"],
                str(add_timestamp()),
                str(add_timestamp()),
                row["game_id"],
                row["player_id"],
                row["goal_keeper"],
                row["selected"],
            ),
        )
