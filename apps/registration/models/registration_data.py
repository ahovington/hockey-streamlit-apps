import pandas as pd

from utils import read_data


def registration_count() -> pd.DataFrame:
    """Extact the registrations count before the start of the season.

    Retuns:
        pd.DataFrame: The results of the query.
    """
    return read_data(
        f"""
            with first_game_dates as (
                select
                    season,
                    date(min(start_ts)) as first_game_date
                from games
                group by
                    season
            ),

            registration_dates as (
                select
                    id,
                    season,
                    registered_date::date as registered_date
                from registrations
            ),

            days_before_first_game as (
                select
                    season,
                    first_game_date,
                    registered_date,
                    registered_date::date - first_game_date::date as days_before_first_game
                from registration_dates
                inner join first_game_dates
                using(season)
            ),

            registration_count as (
                select
                    season,
                    count(*) as total_registrations
                from days_before_first_game
                where
                    days_before_first_game <= 0
                group by
                    season
            )

            select *
            from registration_count
    """
    )


def registration_dates() -> pd.DataFrame:
    """Extact the registrations dates before the start of the season.

    Retuns:
        pd.DataFrame: The results of the query.
    """
    return read_data(
        f"""
            with first_game_dates as (
                select
                    season,
                    date(min(start_ts)) as first_game_date
                from games
                group by
                    season
            ),

            registration_dates as (
                select
                    id,
                    season,
                    team,
                    registered_date::date as registered_date
                from registrations
            ),

            days_before_first_game as (
                select
                    id,
                    season,
                    team,
                    first_game_date,
                    registered_date,
                    registered_date::date - first_game_date::date as days_before_first_game
                from registration_dates
                inner join first_game_dates
                using(season)
            )

            select *
            from days_before_first_game
            where days_before_first_game <= 0
    """
    )
