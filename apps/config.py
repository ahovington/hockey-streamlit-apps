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
        club_name: str
        club_logo: str
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


ASSET_URL_STEM = "https://hockey-assets.s3.ap-southeast-1.amazonaws.com/"


config = Config(
    app=Config.App(
        seasons=["2023", "2024"],
        club_name="West",
        club_logo=f"{ ASSET_URL_STEM }wests.png",
        logo_assets={
            "West": f"{ ASSET_URL_STEM }wests.png",
            "University": f"{ ASSET_URL_STEM }university.jpeg",
            "Tigers": f"{ ASSET_URL_STEM }tigers.png",
            "Souths": f"{ ASSET_URL_STEM }souths.jpeg",
            "Port Stephens": f"{ ASSET_URL_STEM }port_stephens.jpeg",
            "Norths": f"{ ASSET_URL_STEM }norths.jpeg",
            "Maitland": f"{ ASSET_URL_STEM }maitland.png",
            "Gosford": f"{ ASSET_URL_STEM }gosford.png",
            "Crusaders": f"{ ASSET_URL_STEM }crusaders.png",
            "Colts": f"{ ASSET_URL_STEM }colts.png",
        },
        database_lock=False,
    ),
)
