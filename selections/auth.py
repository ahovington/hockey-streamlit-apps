import yaml
from yaml.loader import SafeLoader
import streamlit as st
import streamlit_authenticator as stauth


with open("selections/config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)


def login() -> bool:
    """Login into app

    Returns:
        bool: The result of the login attempt, True if successful.
    """
    authenticator = _authenticator()
    authenticator.login("Login", "main")
    if st.session_state["authentication_status"]:
        col1, _ = st.columns([1, 5])
        authenticator.logout("Logout", "main", key="unique_key")
        if col1.button("Reset password"):
            _reset_password(authenticator)
        return True
    elif st.session_state["authentication_status"] is False:
        st.error("Username/password is incorrect")
        return False
    elif st.session_state["authentication_status"] is None:
        st.warning("Please enter your username and password")
        return False


def _reset_password(authenticator: stauth.Authenticate):
    try:
        if authenticator.reset_password(st.session_state["username"], "Reset password"):
            st.success("Password modified successfully")
            _update_config()
    except Exception as e:
        st.error(e)


def register_user():
    try:
        if authenticator.register_user("Create user", preauthorization=False):
            st.success("User registered successfully")
            _update_config()
    except Exception as e:
        st.error(e)


def _update_config():
    with open("selections/config.yaml", "w") as file:
        yaml.dump(config, file, default_flow_style=False)


def _authenticator() -> stauth.Authenticate:
    return stauth.Authenticate(
        credentials=config["credentials"],
        cookie_name=config["cookie"]["name"],
        key=config["cookie"]["key"],
        cookie_expiry_days=config["cookie"]["expiry_days"],
    )
