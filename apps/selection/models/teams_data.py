from utils import read_data


def team_name_data(season: str):
    return read_data(f"""select distinct team from teams where season = '{season}'""")


def team_id_data(season: str, team: str, grade: str):
    return read_data(
        f"""select id from teams where season = '{season}' and team = '{team}' and grade = '{grade}'"""
    ).iloc[0, 0]
