import datetime as dt
import streamlit as st
import pandas as pd

from utils import read_data, calculate_date_interval


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
        with _selections as (
            select
                game_id,
                sum(selected::int) as selected,
                sum(played::int) as played
            from selections
            group by
                game_id
        )

        select
            g.create_ts,
            g.update_ts,
            g.id as game_id,
            t.team || ' - ' || t.grade as team_name,
            g.opposition,
            g.start_ts,
            g.round,
            s.selected,
            s.played,
            g.goals_for,
            g.goals_against,
            case
                when round = 'SF1' then '30'
                when round = 'PF1' then '40'
                when round = 'GF1' then '30'
                else round
            end as round_order,
            t.team_order
        from games as g
        inner join teams as t
        on g.team_id = t.id
        left join _selections as s
        on g.id = s.game_id
        where { ' '.join(filters) }
        order by
            t.team_order
        """
    ).replace("", None)
    ### Format the game start time ###
    df.loc[:, "game_time"] = pd.to_datetime(df.loc[:, "start_ts"]).dt.strftime(
        "%a %d %B, %-I:%M %p"
    )
    df.loc[:, "start_ts"] = pd.to_datetime(df.loc[:, "start_ts"])
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
            "game_time",
            "selected",
            "played",
            "goals_for",
            "goals_against",
        ]
    ]


def game_selection_data(
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
        order by
            t.team_order
        """
    ).replace("", None)
    ### game validation ###
    if not df.shape[0]:
        return pd.DataFrame()
    df.loc[:, "game_time"] = pd.to_datetime(df.loc[:, "start_ts"]).dt.strftime(
        "%a %d %B, %-I:%M %p"
    )
    return df[["round", "team_name", "opposition", "game_time", "players_selected"]]


def last_game_date(season: str) -> pd.DataFrame:
    read_data(
        f"""
        select max(start_ts) + INTERVAL '1 days' as max_ts
        from games
        where
            season = '{ season }'
            and start_ts < '{ dt.datetime.now() }'
        """
    ).iloc[0, 0]
