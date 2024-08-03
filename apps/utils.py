import os
import string
import random
from dotenv import load_dotenv
from pathlib import Path
from dataclasses import dataclass
from urllib.parse import quote_plus
from typing import Any
import datetime as dt
import pandas as pd
from sqlalchemy import Engine, create_engine, text
import streamlit as st

from pages import login_page, login_create_login


load_dotenv(dotenv_path=Path(".env"))


@dataclass
class Database:
    db_host: str
    db_name: str
    db_password: str
    db_user: str

    @property
    def db_url(self) -> str:
        """Generate the url of the database.

        Returns:
            str: The database url.
        """
        return f"""postgresql://{ self.db_user }:{ quote_plus(self.db_password) }@{ self.db_host}/{ self.db_name }"""

    @property
    def create_db_engine(self) -> Engine:
        """Create database engine

        Returns:
            Engine: Database engine.
        """
        return create_engine(self.db_url)


database = Database(
    db_host=os.getenv("DB_HOST"),
    db_name=os.getenv("DB_NAME"),
    db_password=os.getenv("DB_PASSWORD"),
    db_user=os.getenv("DB_USER"),
)


def auth_validation(func):
    def wrapper():
        if st.session_state.get("authentication_status", False):
            return func()
        _help = "Users need to pre preauthorised before they can create a login.\n\
                Contact the Administrator to be added to the authorised users list."
        st.page_link(
            login_page,
            icon=":material/key:",
            label="Login to access this page",
            help=_help,
        )
        st.page_link(
            login_create_login,
            icon=":material/key:",
            label="Or create a login",
            help=_help,
        )
        return

    return wrapper


def id_generator(size=6, chars: str = string.ascii_uppercase + string.digits) -> str:
    """creaete random id

    Args:
        size (int, optional): The length of the id. Defaults to 6.
        chars (str, optional): (
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
        with database.create_db_engine.connect() as session:
            return pd.read_sql_query(sql_statement, session)
    finally:
        session.close()


def create_data(
    table: str,
    columns: tuple[str],
    values: tuple[Any],
    database_lock: bool = False,
    verbose: bool = False,
) -> None:
    """Helper function to write a row of data to the database

    Args:
        table (str): The table to write to.
        columns (tuple(str)): The columns to add a row for.
        values (tuple(Any)): The values to write.
        database_lock (bool, optional): If the database has been locked.
        verbose (bool, optional): True to print the queries written to the database.

    Returns: None
    """
    if database_lock:
        st.error(
            "A hard lock has been applied to the databases. Contact the administrator."
        )
        return
    try:
        with database.create_db_engine.connect() as session:
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
    database_lock: bool = False,
    verbose: bool = False,
) -> None:
    """Helper function to update a row of data in the database

    Args:
        table (str): The table to update.
        column (str): The column to update.
        row_id (str): The id of the record to update.
        value (Any): The new value.
        value_string_type (bool, optional): True if the value is of string type.
        database_lock (bool, optional): If the database has been locked.
        verbose (bool, optional): True to print the queries written to the database.

    Returns: None
    """
    # TODO: Add user to the change
    if database_lock and table != "users":
        st.error(
            "A hard lock has been applied to the databases. Contact the administrator."
        )
        return
    try:
        sql = f"""UPDATE { table } SET { column } = { value }, update_ts = '{ add_timestamp() }' WHERE id = '{ row_id }'"""
        if value_string_type:
            sql = f"""UPDATE { table } SET { column } = '{ value }', update_ts = '{ add_timestamp() }' WHERE id = '{ row_id }'"""
        with database.create_db_engine.connect() as session:
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
    return f"""${ input :,.1f}"""


def select_box_query(
    name: str, options: list[str], location: st.columns, placeholder: str = ""
):
    # TODO: reimplement query params
    page_index = None if placeholder else 0
    # query_param = st.query_params.get(name)
    # if query_param and query_param in options:
    #     page_index = options.index(query_param)
    selection = location.selectbox(
        f"Select { name }", options, index=page_index, placeholder=placeholder
    )
    # st.query_params[name] = selection
    # if not selection:
    #     del st.query_params[name]
    return selection


def clean_query_params(filters: list[str]):
    # TODO: reimplement query params
    params = st.query_params.to_dict()
    for param in params:
        if param in filters:
            continue
        del st.query_params[param]


def team_name_clean(team_name: str) -> str:
    _team_name = team_name.upper()
    if "WEST" in _team_name:
        return "West"
    if "UNI" in _team_name:
        return "University"
    if "TIGER" in _team_name:
        return "Tigers"
    if "SOUTH" in _team_name:
        return "Souths"
    if "UNI" in _team_name:
        return "University"
    if "PORT" in _team_name:
        return "Port Stephens"
    if "NORTH" in _team_name:
        return "Norths"
    if "MAITLAND" in _team_name:
        return "Maitland"
    if "GOSFORD" in _team_name:
        return "Gosford"
    if "CRUSADER" in _team_name:
        return "Crusaders"
    if "COLT" in _team_name:
        return "Colts"
