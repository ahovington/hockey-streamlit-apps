from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Config:
    app: App

    @dataclass
    class App:
        seasons: list[str]
        club_name: str
        club_logo: str
        logo_assets: dict[str, str]
        user_groups: list[str]
        database_lock: bool = True


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
        user_groups=["admin", "committee_member", "collector"],
        database_lock=False,
    ),
)
