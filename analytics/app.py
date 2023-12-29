import streamlit as st


def todo(*args):
    st.title("App to do list")

    st.subheader("Analytics")
    st.write("- Player profile")
    st.write("- Club statistics")
    st.write("- Team statistics")
    st.write("- Player statistics")

    st.subheader("Databases")
    st.write("- Add users to track who made a change")
    st.write("- Research db writing concurrency")


apps = {"TODO:": todo}
if __name__ == "__main__":
    st.set_page_config(
        page_title="Newcastle West Hockey Finance App",
        page_icon="https://cdn.revolutionise.com.au/cups/whc/files/ptejzkfy3k8qvtlg.ico",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    with st.sidebar:
        season = st.selectbox("Season", ["2023", "2024"])

    col1, col2 = st.columns([2, 3])
    col1.image("./rosella.png")
    app_name = tuple(apps.keys())[0]
    app_name = col2.selectbox("Select page", tuple(apps.keys()))
    apps[app_name](season)
