from utils import read_data


def field_name_data():
    return read_data("""select field from locations""")
