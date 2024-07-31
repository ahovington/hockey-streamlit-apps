import streamlit as st
from dotenv import load_dotenv
from pathlib import Path

from config import Config
from utils import select_box_query
from results.app import App as restults_app
from selections.app import App as selections_app
from registrations.app import App as registrations_app
from finance.app import App as finance_app


load_dotenv(dotenv_path=Path(".env"))


ASSET_URL_STEM = "https://hockey-assets.s3.ap-southeast-1.amazonaws.com/"


config = Config(
    app=Config.App(
        seasons=["2023", "2024"],
        west_logo_url=f"{ ASSET_URL_STEM }wests.png",
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

apps = {
    "Results": restults_app,
    "Registrations": registrations_app,
    "Selections": selections_app,
    "Finance": finance_app,
}

if __name__ == "__main__":
    st.set_page_config(
        page_title="Newcastle West Hockey",
        page_icon=config.app.west_logo_url,
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    with st.sidebar:
        app_name = select_box_query("Application", tuple(apps.keys()), st)
    apps[app_name](config)
