from __future__ import annotations
from dataclasses import dataclass
from urllib.parse import quote_plus


@dataclass
class App:
    database_lock: bool = True


@dataclass
class Database:
    db_host: str
    db_name: str
    db_password: str
    db_user: str

    def db_url(self) -> str:
        return f"postgresql://{ self.db_user }:{ quote_plus(self.db_password) }@{ self.db_host}/{ self.db_name }"
