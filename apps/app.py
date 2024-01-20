import streamlit as st

from utils import config
from results.app import App as restults_app
from selections.app import App as selections_app
from finance.app import App as finance_app

apps = {
    "Results": restults_app,
    "Registrations": finance_app,
    "Selections": selections_app,
}

if __name__ == "__main__":
    st.set_page_config(
        page_title="Newcastle West Hockey",
        page_icon=config.app.west_logo_url,
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    with st.sidebar:
        app_name = st.selectbox("Select page", tuple(apps.keys()))

    apps[app_name]()
