import streamlit as st

from game_results import GameResults

apps = {"Game results": GameResults}

if __name__ == "__main__":
    st.set_page_config(
        page_title="Results App Newcastle West Hockey",
        page_icon="https://cdn.revolutionise.com.au/cups/whc/files/ptejzkfy3k8qvtlg.ico",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    col1, col2 = st.columns([3, 7])
    col1.image("./assets/wests.png")
    col2.title("West Hockey Results")

    APP_NAME = tuple(apps.keys())[0]
    APP_NAME = col2.selectbox("Select page", tuple(apps.keys()))
    apps[APP_NAME]()
