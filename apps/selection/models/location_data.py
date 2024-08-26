import pandas as pd

from utils import read_data


def location_name_data() -> pd.DataFrame:
    return read_data("""select distinct name from locations""")


def location_id_data(location: str, field: str) -> pd.DataFrame:
    return read_data(
        f"""select id from locations where name = '{location}' and field = '{field}'"""
    )
