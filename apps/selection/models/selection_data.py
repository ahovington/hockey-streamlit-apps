import datetime as dt
import streamlit as st
import pandas as pd

from utils import read_data, calculate_date_interval


def selections_input_data(season: str, team_round: str, team: str):
    """Extact the selections data for the team and round.

    Args:
        season (str): The hockey season, usually the calendar year.
        team_round (str): The teams round of the season.
        team (str): The team being selected for.

    Retuns:
        pd.DataFrame: The results of the query.
    """
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
            on p.id = r.player_id
            cross join _games as g
            where
                r.season = '{ season }'
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
        return pd.DataFrame()
    return df


def selections_output_data(
    season: str, date_end: dt.datetime, date_inteval: int = 6
) -> pd.DataFrame:
    """Extact the selections made for the week.

    Args:
        season (str): The hockey season, usually the calendar year.
        date_end (dt.datetime): The end timestamp.
        date_inteval (int, optional): How many days before the date_end to include. Defualts to 6.

    Retuns:
        pd.DataFrame: The results of the query.
    """
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
            """
            There are no selections for this date range.
            If there are games showing, ensure players have been selected for those games.
            """
        )
        return pd.DataFrame()
    df.loc[:, "game_time"] = pd.to_datetime(df.loc[:, "start_ts"]).dt.strftime(
        "%a %d %B, %-I:%M %p"
    )
    return df
