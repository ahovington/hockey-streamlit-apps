from __future__ import annotations
from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import quote_plus

load_dotenv(dotenv_path=Path(".env"))


@dataclass
class Config:
    app: App
    database: Database

    @dataclass
    class App:
        west_logo_url: str
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
