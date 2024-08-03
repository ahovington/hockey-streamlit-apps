import pandas as pd

from utils import read_data


def field_name_data() -> pd.DataFrame:
    return read_data("""select field from locations""")
