from utils import read_data


def location_name_data():
    return read_data("""select name from locations""")


def location_id_data(location: str, field: str):
    return read_data(
        f"""select id from locations where name = '{location}' and field = '{field}'"""
    ).iloc[0, 0]
