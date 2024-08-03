import pandas as pd

from utils import read_data


def team_data(season: str) -> pd.DataFrame:
    """Extact the teams for the current season.

    Args:
        season (str): The hockey season, usually the calendar year.

    Retuns:
        pd.DataFrame: The results of the query.
    """
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
