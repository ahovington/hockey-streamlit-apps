import os
import string
import random
from typing import Any
import datetime as dt
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

from config import Config


config = Config(
    app=Config.App(
        seasons=["2023", "2024"],
        west_logo_url="https://hockey-assets.s3.ap-southeast-1.amazonaws.com/wests.png",
        database_lock=False,
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


def id_generator(size=6, chars=string.ascii_uppercase + string.digits) -> str:
    """creaete random id

    Args:
        size (int, optional): The length of the id. Defaults to 6.
        chars (_type_, optional): (
            The characters included in the id.
            Defaults to string.ascii_uppercase+string.digits.
        )

    Returns:
        str: The random id
    """
    return "".join(random.choice(chars) for _ in range(size))


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
        sql = f"""UPDATE { table } SET { column } = { value }, update_ts = '{ add_timestamp() }' WHERE id = '{ row_id }'"""
        if value_string_type:
            sql = f"""UPDATE { table } SET { column } = '{ value }', update_ts = '{ add_timestamp() }' WHERE id = '{ row_id }'"""
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


def add_timestamp() -> pd.to_datetime:
    """Calculates the current timestamp in isoformat.

    Returns:
        pd.to_datetime: The current timestamp in isoformat
    """
    return pd.to_datetime(dt.datetime.now().isoformat())


def compare_dataframes(
    oringinal_df: pd.DataFrame, updated_df: pd.DataFrame, primary_key: str
) -> pd.DataFrame:
    """Take two dataframe and return the rows that have changed.
    Both data frame are requred to have the same schema.

    Args:
        oringinal_df (pd.DataFrame): The dataframe before the change process.
        updated_df (pd.DataFrame): The dataframe after the change process.
        primary_key (str): The primary key common to both dataframes.
    """
    if not (oringinal_df.columns == updated_df.columns).all():
        raise ValueError("Dataframes need to have identical schemas")
    changed_df = pd.concat([oringinal_df, updated_df]).drop_duplicates(keep=False)
    return updated_df[updated_df[primary_key].isin(changed_df[primary_key].unique())]


def calculate_date_interval(
    date_end: dt.datetime, date_inteval: int = 6, date_filter=True
) -> tuple[str, str]:
    """Calculate the start date based on the end date and a interval.

    Args:
        date_end (dt.datetime): The end date.
        date_inteval (int, optional): The interval in days. Defaults to 6.
        date_filter (bool, optional): True to format the dates for use in SQL. Defaults to True.

    Returns:
        tuple[str, str]: The start and end date of the period.
    """
    date_end = date_end + dt.timedelta(days=1)
    date_start = date_end - dt.timedelta(days=date_inteval)
    if date_filter:
        return (
            date_start.strftime("%Y-%m-%d %H:%M:%S"),
            date_end.strftime("%Y-%m-%d %H:%M:%S"),
        )
    return (date_start.strftime("%d %B"), date_end.strftime("%d %B"))


def financial_string_formatting(input: Any):
    return f"""${ input :.1f}"""


def select_box_query(
    name: str, options: list[str], location: st.columns, placeholder: str = ""
):
    page_index = None if placeholder else 0
    if st.query_params.get(name) and st.query_params.get(name) in options:
        page_index = options.index(st.query_params[name])
    selection = location.selectbox(
        f"Select { name }", options, index=page_index, placeholder=placeholder
    )
    st.query_params[name] = selection
    if not selection:
        del st.query_params[name]
    return selection


def clean_query_params(filters: list[str]):
    params = st.query_params.to_dict()
    for param in params:
        if param in filters:
            continue
        del st.query_params[param]
