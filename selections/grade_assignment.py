import streamlit as st
import numpy as np
import pandas as pd

from utils import compare_dataframes, read_data, update_data


def GradeAssignment(database_lock: bool, season: str):
    st.title("Assign players a team and grade")
    st.subheader(
        "Team assignments are only to help with selections and can be changed at any time.",
        divider="green",
    )

    st.subheader("Allocate players to one of the following teams.")

    team = team_data(season)
    if not team.shape[0]:
        st.error(f"No team data available for { season }")
        return

    # return updated table and identify changes
    _team = team.drop(columns=["full_team_name"])
    updated_team = input_team_table(_team)
    team_changes = compare_dataframes(_team, updated_team, "team_id")

    player = player_data(season)
    if not player.shape[0]:
        st.error(f"No player data available for { season }")
        return

    updated_player = input_player_team_table(player, team["full_team_name"].unique())
    player_changes = compare_dataframes(player, updated_player, "registration_id")

    # Refresh data after making changes
    if st.button("refresh page"):
        team = team_data(season)
        player = player_data(season)

    # update team rows
    if team_changes.shape[0]:
        st.write("Update team data", team_changes)
        update_team_data(team_changes, lock=database_lock)

    if player_changes.shape[0]:
        st.write("Update player data", player_changes)

        update_default_team(
            player_changes.merge(
                team[["team_id", "full_team_name"]],
                left_on="team",
                right_on="full_team_name",
                how="inner",
            )
            .drop(columns=["full_team_name"], axis=1)
            .replace("", np.nan),
            lock=database_lock,
        )


def team_data(season: str):
    return read_data(
        f"""
        select
            id as team_id,
            grade,
            team,
            manager,
            manager_mobile,
            team || ' - ' || grade as full_team_name,
            team_order
        from teams
        where
            season = '{ season }'
        order by
            team_order,
            grade
    """
    )


def input_team_table(df: pd.DataFrame) -> pd.DataFrame:
    team_id = df["team_id"]
    _df = df.drop(columns=["team_id"], axis=1)
    with st.form("Teams"):
        result = st.data_editor(
            _df,
            disabled=["grade" "team"],
            hide_index=True,
            use_container_width=True,
        )
        result.loc[:, "team_id"] = team_id
        commit_changes = st.form_submit_button("Submit")
    if not commit_changes:
        return df
    return result[df.columns]


def update_team_data(df: pd.DataFrame, lock: bool = True):
    if lock:
        st.error("Database is locked, contact the administrator.")
        return
    for _, row in df.iterrows():
        update_data(
            "teams", "manager", row["team_id"], row["manager"], value_string_type=True
        )
        update_data(
            "teams",
            "manager_mobile",
            row["team_id"],
            row["manager_mobile"],
            value_string_type=True,
        )
        update_data("teams", "team_order", row["team_id"], row["team_order"])


def player_data(season: str):
    return read_data(
        f"""
        select
            r.id as registration_id,
            p.full_name as players_name,
            r.team,
            r.grade
        from players as p
        inner join registrations as r
        on p.id = r.national_id
        where
            r.season = '{ season }'
        order by
            r.team
    """
    )


def input_player_team_table(df: pd.DataFrame, team_names: list[str]) -> pd.DataFrame:
    registration_id = df["registration_id"]
    _df = df.drop("registration_id", axis=1)
    with st.form("Grade Assignments"):
        result = st.data_editor(
            _df,
            column_config={
                "team": st.column_config.SelectboxColumn(
                    "team name",
                    help="Players default grade.",
                    width="medium",
                    default="",
                    options=team_names,
                ),
            },
            disabled=["players_name"],
            hide_index=True,
            use_container_width=True,
        )
        result.loc[:, "registration_id"] = registration_id
        result.loc[result["grade"].isna(), "grade"] = (
            result["team"].str.split("-").str[-1]
        )
        commit_changes = st.form_submit_button("Submit")
    if not commit_changes:
        return df
    return result[df.columns]


def update_default_team(df: pd.DataFrame, lock: bool = True):
    if lock:
        st.error("Database is locked, contact the administrator.")
        return
    for _, row in df.iterrows():
        update_data("registrations", "team_id", row["registration_id"], row["team_id"])
        update_data("registrations", "team", row["registration_id"], row["team"])
        update_data("registrations", "grade", row["registration_id"], row["grade"])
