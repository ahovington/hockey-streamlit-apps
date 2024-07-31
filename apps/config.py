from __future__ import annotations
from dataclasses import dataclass
from urllib.parse import quote_plus
from sqlalchemy import create_engine, Engine


@dataclass
class Config:
    app: App

    @dataclass
    class App:
        seasons: list[str]
        west_logo_url: str
        logo_assets: dict[str, str]
        database_lock: bool = True


@dataclass
class Database:
    db_host: str
    db_name: str
    db_password: str
    db_user: str

    def db_url(self) -> str:
        """Generate the url of the database.

        Returns:
            str: The database url.
        """
        return f"""postgresql://{ self.db_user }:{ quote_plus(self.db_password) }@{ self.db_host}/{ self.db_name }"""

    def create_db_engine(self) -> Engine:
        """Create database engine

        Returns:
            Engine: Database engine.
        """
        return create_engine(self.db_url())
