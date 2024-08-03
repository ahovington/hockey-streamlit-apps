import pandas as pd

from utils import read_data


def grade_name_data(season: str) -> pd.DataFrame:
    return read_data(f"""select grade from teams where season = '{season}'""")
