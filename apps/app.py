import streamlit as st

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
        # page_icon=config.app.west_logo_url,
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    with st.sidebar:
        database_lock = st.toggle("Lock database", True)
        season = st.selectbox("Season", ["2023", "2024"])
        APP_NAME = st.selectbox("Select page", tuple(apps.keys()))
        apps[APP_NAME](database_lock, season)
