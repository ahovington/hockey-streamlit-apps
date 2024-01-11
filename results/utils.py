import os
import pandas as pd

from config import Config

config = Config(
    app=Config.App(
        west_logo_url="https://hockey-assets.s3.ap-southeast-1.amazonaws.com/wests.png",
    ),
    database=Config.Database(
        db_host=os.getenv(
            "DB_HOST", "dpg-cm5o187qd2ns73eplb8g-a.singapore-postgres.render.com"
        ),
        db_name=os.getenv("DB_NAME", "hockey_services"),
        db_password=os.getenv("DB_PASSWORD", ""),
        db_user=os.getenv("DB_USER", "ahovington"),
    ),
)

engine = config.database.create_db_engine()

asset_url_stem = "https://hockey-assets.s3.ap-southeast-1.amazonaws.com/"
assets = {
    "West Green": f"{ asset_url_stem }wests.png",
    "West Red": f"{ asset_url_stem }wests.png",
    "West": f"{ asset_url_stem }wests.png",
    "University": f"{ asset_url_stem }university.jpeg",
    "University Trains": f"{ asset_url_stem }university.jpeg",
    "Tigers": f"{ asset_url_stem }tigers.png",
    "Tiger": f"{ asset_url_stem }tigers.png",
    "Souths": f"{ asset_url_stem }souths.jpeg",
    "Port Stephens": f"{ asset_url_stem }port_stephens.jpeg",
    "Norths Dark": f"{ asset_url_stem }norths.jpeg",
    "Norths Light": f"{ asset_url_stem }norths.jpeg",
    "Norths": f"{ asset_url_stem }norths.jpeg",
    "North": f"{ asset_url_stem }norths.jpeg",
    "Maitland": f"{ asset_url_stem }maitland.png",
    "Gosford": f"{ asset_url_stem }gosford.png",
    "Crusaders": f"{ asset_url_stem }crusaders.png",
    "Colts": f"{ asset_url_stem }colts.png",
}


# Function to create a SQLite connection and retrieve data
def read_data(sql_statement: str) -> pd.DataFrame:
    """Help function to read data from the database.

    Args:
        sql_statement (str): The SQL statement to pass to the db.

    Returns:
        pd.DataFrame: A pandas dataframe containing the results.
    """
    try:
        with engine.connect() as session:
            return pd.read_sql_query(sql_statement, session)
    finally:
        session.close()
