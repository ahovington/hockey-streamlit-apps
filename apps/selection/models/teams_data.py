import pandas as pd

from utils import read_data


def team_data(season: str) -> pd.DataFrame:
    return read_data(f"""select team, grade from teams where season = '{season}'""")


def team_id_data(season: str, team: str, grade: str) -> pd.DataFrame:
    return read_data(
        f"""select id from teams where season = '{season}' and team = '{team}' and grade = '{grade}'"""
    )
