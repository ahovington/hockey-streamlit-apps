import pandas as pd

from utils import read_data


def player_data(season: str) -> pd.DataFrame:
    """Extact the registered players for the current season.

    Args:
        season (str): The hockey season, usually the calendar year.

    Retuns:
        pd.DataFrame: The results of the query.
    """
    return read_data(
        f"""
        select
            r.id as registration_id,
            p.full_name as players_name,
            r.team,
            r.grade,
            t.team_order
        from players as p
        inner join registrations as r
        on p.id = r.player_id
        left join teams as t
        on t.id = r.team_id
        where
            r.season = '{ season }'
        order by
            r.team
    """
    )
