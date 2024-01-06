import os
import string
import random
from typing import Any, Optional
import datetime as dt
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

from config import Config


config = Config(
    app=Config.App(database_lock=True),
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

asset_url_stem = "https://cdn.revolutionise.com.au/logos/"
asset_norths = "https://scontent-syd2-1.xx.fbcdn.net/v/t39.30808-6/303108111_594953908808882_8195829583102730483_n.jpg?_nc_cat=103&ccb=1-7&_nc_sid=efb6e6&_nc_ohc=3mXcO3Igh1oAX92MBFS&_nc_ht=scontent-syd2-1.xx&oh=00_AfAJideVNofqudUjcWqNERY5ZCgdILdeiG3FHI1F-6V6hg&oe=659D6046"
assets = {
    "4thGreen": f"{ asset_url_stem }tqbgdyotasa2pwz4.png",
    "4thRed": f"{ asset_url_stem }tqbgdyotasa2pwz4.png",
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
    date_start = date_end - dt.timedelta(days=date_inteval)
    if date_filter:
        return (date_start.strftime("%Y%m%d"), date_end.strftime("%Y%m%d"))
    return (date_start.strftime("%d %B"), date_end.strftime("%d %B"))


def results_data(
    season: str, team: Optional[str] = None, game_round: Optional[str] = None
) -> pd.DataFrame:
    """Extact the outstanding club fees.

    Args:
        season (str): The hockey season, usually the calendar year.
        team (str, optional): The teams name.
        game_round (str, optional): The round of the season.

    Retuns:
        pd.DataFrame: The results of the query.
    """
    filters = ["where", f"g.season = '{ season }'"]
    if team:
        filters.append("and")
        filters.append(f"t.team || ' - ' || t.grade = '{ team }'")
    if game_round:
        filters.append("and")
        filters.append(f"g.round = '{ game_round }'")
    df = read_data(
        f"""
        select
            g.id,
            t.team,
            t.grade,
            t.team || ' - ' || t.grade as team_name,
            g.season,
            g.round,
            case
                when l.name = 'Newcastle International Hockey Centre'
                then 'NIHC'
                else l.name
            end as location_name,
            l.field,
            g.finals,
            case
                when g.opposition = '4thGreen' then 'West Green'
                when g.opposition = '4thRed' then 'West Red'
                else g.opposition 
            end as opposition,
            g.start_ts,
            g.goals_for,
            g.goals_against
        from games as g
        left join teams as t
        on g.team_id = t.id
        left join locations as l
        on g.location_id = l.id
        { " ".join(filters) }
        """
    )
    df.loc[:, "goals_for"] = (
        df.loc[:, "goals_for"].replace("", 0).astype(float).astype(int)
    )
    df.loc[:, "goals_against"] = (
        df.loc[:, "goals_against"].replace("", 0).astype(float).astype(int)
    )
    df.loc[df["goals_for"] > df["goals_against"], "result"] = "Win"
    df.loc[df["goals_for"] < df["goals_against"], "result"] = "Loss"
    df.loc[df["goals_for"] == df["goals_against"], "result"] = "Draw"

    return df
