import logging
from typing import Any, Protocol
from sqlalchemy import text
from sqlalchemy.orm import Session
import pandas as pd

from .utils import add_timestamp


class LoadFromCSV(Protocol):
    def validate() -> bool:
        ...

    def load():
        ...

    def update():
        ...

    def purge():
        ...


class Teams(LoadFromCSV):
    TABLE = "teams"
    DB_COLUMNS = ["id", "create_ts", "update_ts"]
    REQUIRED_SOURCE_COLUMNS = [
        "season",
        "grade",
        "team",
    ]
    ADDITIONAL_SOURCE_COLUMNS = ["manager", "manager_mobile"]

    def __init__(self, session: Session, source_data_filename: str):
        self.session = session
        self.source_data_filename = source_data_filename
        self.df = self._read_data()
        self.validate()

    def validate(self) -> bool:
        """
        Checks:
            - All mandatory columns present.
            - No Nulls for mandatory columns.
        Returns: True if validations successful, False if failed.
        """
        df = self.df[Teams.REQUIRED_SOURCE_COLUMNS]
        res = df.isna().sum() > 0
        if res.values.sum():
            logging.warning(
                f"The following columns have missing values: {', '.join((res[res==True].index))}"
            )
            return False
        else:
            logging.info("Source data validation completed succesfully")
            return True

    def load(self):
        logging.info("Loading new records")
        insert_columns = Teams.DB_COLUMNS + Teams.REQUIRED_SOURCE_COLUMNS
        values = self._values_to_load(Teams.DB_COLUMNS + Teams.REQUIRED_SOURCE_COLUMNS)
        if not values:
            logging.info("No new records")
            pass
        for value in values:
            self.session.execute(
                text(
                    f"""
                    INSERT INTO {Teams.TABLE} ({','.join(insert_columns)})
                    VALUES
                        {value}
                    """
                )
            )
            self.session.commit()

    def update(self):
        logging.info("Updating records")
        insert_columns = (
            Teams.DB_COLUMNS
            + Teams.REQUIRED_SOURCE_COLUMNS
            + Teams.ADDITIONAL_SOURCE_COLUMNS
        )
        insert_columns.remove("create_ts")
        for update_values in self._changed_values(insert_columns):
            for id, update_value in update_values.items():
                for column, value in update_value.items():
                    logging.info(f"Updating {id}, {column}: {value}")
                    self.session.execute(
                        text(
                            f"""
                            UPDATE {Teams.TABLE}
                            SET {column} = '{value}'
                            WHERE id = '{id}'
                            """
                        )
                    )
                    self.session.commit()

    def purge(self):
        query = f"""DELETE FROM {Teams.TABLE}"""
        self.session.execute(text(query))
        self.session.commit()

    def _read_data(self):
        logging.info(f"Reading in data from {self.source_data_filename}")
        df = pd.read_csv(self.source_data_filename)
        df = df.fillna("")
        df.loc[:, "id"] = self._add_primary_key(df)
        df.loc[:, "create_ts"] = add_timestamp()
        df.loc[:, "update_ts"] = add_timestamp()
        return df

    def _values_to_load(self, columns: list[str], update=False) -> list[tuple[Any]]:
        """
        Build SQL query to insert data into db.
        """
        # Return column ids already loded.
        ids = list(
            map(
                lambda x: x[0],
                self.session.execute(text(f"select id from {Teams.TABLE}")).fetchall(),
            )
        )
        df = self.df[~self.df["id"].isin(ids)][columns]
        if update:
            df = self.df[self.df["id"].isin(ids)][columns]
        insert_rows = []
        if df.shape[0]:
            for _, row in df.iterrows():
                insert_rows.append(tuple(row.values))
        return insert_rows

    def _changed_values(self, columns: list[str]):
        values = self._values_to_load(columns, update=True)
        changed_values = []
        for value in values:
            update_dict = {}
            for i, column in enumerate(columns):
                if not value[i]:
                    continue
                if i == 0:
                    id = value[i]
                    continue
                # Check if values have changed
                current_state = self.session.execute(
                    text(f"select {column} from {Teams.TABLE} where id = '{id}'")
                ).first()
                if not current_state:
                    continue
                if str(current_state[0]) != str(value[i]):
                    # Record columns that have changed
                    update_dict[column] = value[i]
            if len(update_dict.keys()) <= 1:
                # if only thes update_ts has changed continue
                continue
            values = {id: update_dict}
            changed_values.append(values)
        return changed_values

    def _add_primary_key(self, df: pd.DataFrame):
        return (
            df["season"].astype(str)
            + df["grade"].astype(str)
            + df["team"].str.replace(" ", "")
        )
