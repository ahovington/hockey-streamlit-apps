import pandas as pd

from utils import read_data


def registration_count() -> pd.DataFrame:
    """Extact the registrations count before the start of the season.

    Retuns:
        pd.DataFrame: The results of the query.
    """
    return read_data(
        f"""
            with registration_count as (
                select
                    season,
                    count(*) as total_registrations
                from registrations
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
            with registration_dates as (
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
                    -- Set the first game date as a constant each year
                    MAKE_DATE(
                        season::integer, 3, 31
                    ) as first_game_date,
                    registered_date
                from registration_dates
            )

            select
                *,
                registered_date::date - first_game_date::date as days_before_end_of_march
            from days_before_first_game
            where registered_date::date - first_game_date::date <= 0
    """
    )
