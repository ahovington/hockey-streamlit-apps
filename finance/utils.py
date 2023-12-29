import os
import string
import random
from typing import Any, Dict
import datetime as dt
import pandas as pd
from urllib.parse import quote_plus
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import streamlit as st

DB_HOST = os.getenv(
    "DB_HOST", "dpg-cm5o187qd2ns73eplb8g-a.singapore-postgres.render.com"
)
DB_NAME = os.getenv("DB_NAME", "hockey_services")
DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD", ""))
DB_USER = "ahovington"
DB_URL = "postgresql://%s:%s@%s/%s" % (
    DB_USER,
    quote_plus(DB_PASSWORD),
    DB_HOST,
    DB_NAME,
)
engine = create_engine(DB_URL)


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


# Function to create a SQLite connection and retrieve data
def read_data(sql_statement: str) -> pd.DataFrame:
    try:
        with engine.connect() as session:
            return pd.read_sql_query(sql_statement, session)
    finally:
        session.close()


def create_data(table: str, columns: tuple[str], values: tuple[Any]):
    try:
        with engine.connect() as session:
            # Update a record
            sql = f"""INSERT INTO { table } ({', '.join(columns) }) VALUES { values }"""
            st.write(sql)
            session.execute(sql)

        # Commit changes
        session.commit()
        st.write(f"Record created successfully to { columns } = { values }")
    finally:
        session.close()


def update_data(table: str, column: str, id: str, value: Any):
    # TODO: Add user to the change
    try:
        with engine.connect() as session:
            # Update a record
            sql = f"""UPDATE { table } SET { column } = ?, update_ts = '{ add_timestamp() }' WHERE id = ?"""
            session.execute(sql, (value, id))

        # Commit changes
        session.commit()
        st.write(f"Record { id } updated successfully to {column} = { value }")
    finally:
        session.close()


def add_timestamp() -> str:
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
    date_end: dt.datetime, date_inteval: int = 6, filter=True
) -> Dict[str, tuple[str, str]]:
    date_start = date_end - dt.timedelta(days=date_inteval)
    if filter:
        return (date_start.strftime("%Y%m%d"), date_end.strftime("%Y%m%d"))
    return (date_start.strftime("%d %B"), date_end.strftime("%d %B"))
