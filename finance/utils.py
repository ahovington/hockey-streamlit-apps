import os
from typing import Any
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

from config import Config


config = Config(
    app=Config.App(
        west_logo_url="https://hockey-assets.s3.ap-southeast-1.amazonaws.com/wests.png"
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

engine = create_engine(config.database.db_url())


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


def update_data(
    table: str,
    column: str,
    row_id: str,
    value: Any,
    value_string_type: bool = False,
    verbose: bool = False,
) -> None:
    """Helper function to update a row of data in the database

    Args:
        table (str): The table to update.
        column (str): The column to update.
        row_id (str): The id of the record to update.
        value (Any): The new value.
        value_string_type (bool, optional): True if the value is of string type.
        verbose (bool, optional): True to print the queries written to the database.

    Returns: None
    """
    # TODO: Add user to the change
    if config.app.database_lock and table != "users":
        st.error(
            "A hard lock has been applied to the databases. Contact the administrator."
        )
        return
    try:
        sql = f"""UPDATE { table } SET { column } = { value } WHERE id = '{ row_id }'"""
        if value_string_type:
            sql = f"""UPDATE { table } SET { column } = '{ value }' WHERE id = '{ row_id }'"""
        with engine.connect() as session:
            # Update a record
            session.execute(text(sql))
            # Commit changes
            session.commit()
        if verbose:
            st.write(sql)
            st.write(
                f"Record { row_id } updated successfully to { column } = { value }"
            )
    finally:
        session.close()


def finacial_string_formatting(input: Any):
    return f"""${ input :.1f}"""
