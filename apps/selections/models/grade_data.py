from utils import read_data


def grade_name_data(season: str):
    return read_data(f"""select grade from teams where season = '{season}'""")
