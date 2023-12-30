import yaml
from yaml.loader import SafeLoader
import streamlit as st
import streamlit_authenticator as stauth


with open("selections/config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"], config["cookie"]["name"], config["cookie"]["key"]
)


def login() -> bool:
    """Login into app

    Returns:
        bool: The result of the login attempt, True if successful.
    """
    authenticator.login("Login", "main")
    if st.session_state["authentication_status"]:
        col1, _ = st.columns([1, 5])
        authenticator.logout("Logout", "main", key="unique_key")
        if col1.button("Reset password"):
            _reset_password()
        return True
    elif st.session_state["authentication_status"] is False:
        st.error("Username/password is incorrect")
        return False
    elif st.session_state["authentication_status"] is None:
        st.warning("Please enter your username and password")
        return False


def _reset_password():
    try:
        if authenticator.reset_password(st.session_state["username"], "Reset password"):
            st.success("Password modified successfully")
    except Exception as e:
        st.error(e)


def register_user():
    try:
        if authenticator.register_user("Create user", preauthorization=False):
            st.success("User registered successfully")
    except Exception as e:
        st.error(e)
