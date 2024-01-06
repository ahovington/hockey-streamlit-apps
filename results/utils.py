import os
from typing import Any, Optional
import pandas as pd
from sqlalchemy import text
import streamlit as st

from config import Config

config = Config(
    app=Config.App(
        west_logo_url="https://cdn.revolutionise.com.au/logos/tqbgdyotasa2pwz4.png",
        database_lock=True,
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

asset_url_stem = "https://cdn.revolutionise.com.au/logos/"
asset_norths = "https://scontent-syd2-1.xx.fbcdn.net/v/t39.30808-6/303108111_594953908808882_8195829583102730483_n.jpg?_nc_cat=103&ccb=1-7&_nc_sid=efb6e6&_nc_ohc=3mXcO3Igh1oAX92MBFS&_nc_ht=scontent-syd2-1.xx&oh=00_AfAJideVNofqudUjcWqNERY5ZCgdILdeiG3FHI1F-6V6hg&oe=659D6046"
assets = {
    "West Green": f"{ asset_url_stem }tqbgdyotasa2pwz4.png",
    "West Red": f"{ asset_url_stem }tqbgdyotasa2pwz4.png",
    "West": f"{ asset_url_stem }tqbgdyotasa2pwz4.png",
    "Port Stephens": f"{ asset_url_stem }lilbc4vodqtkx3uq.jpg",
    "Souths": f"{ asset_url_stem }ktxvg5solvqxq8yv.jpg",
    "Tigers": f"{ asset_url_stem }ksbq9xvnjatt1drb.png",
    "Tiger": f"{ asset_url_stem }ksbq9xvnjatt1drb.png",
    "Maitland": f"{ asset_url_stem }gfnot4z2fginovwo.png",
    "University": f"{ asset_url_stem }3eo6ghaoxwyblbhv.jpg",
    "University Trains": f"{ asset_url_stem }3eo6ghaoxwyblbhv.jpg",
    "Norths Dark": asset_norths,
    "Norths Light": asset_norths,
    "Norths": asset_norths,
    "North": asset_norths,
    "Gosford": f"{ asset_url_stem }4nymemn5sfvawrqu.png",
    "Crusaders": f"{ asset_url_stem }p4ktpeyrau8auvro.png",
    "Colts": f"{ asset_url_stem }nuopppokzejl0im6.png",
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


def create_data(
    table: str, columns: tuple[str], values: tuple[Any], verbose: bool = False
) -> None:
    """Helper function to write a row of data to the database

    Args:
        table (str): The table to write to.
        columns (tuple(str)): The columns to add a row for.
        values (tuple(Any)): The values to write.
        verbose (bool, optional): True to print the queries written to the database.

    Returns: None
    """
    if config.app.database_lock:
        st.error(
            "A hard lock has been applied to the databases. Contact the administrator."
        )
        return
    try:
        with engine.connect() as session:
            # Update a record
            sql = f"""INSERT INTO { table } ({', '.join(columns) }) VALUES { values }"""
            session.execute(text(sql))
            # Commit changes
            session.commit()
        if verbose:
            st.write(sql)
            st.write(f"Record created successfully to { columns } = { values }")
    finally:
        session.close()
