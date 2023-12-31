import yaml
from yaml.loader import SafeLoader
import streamlit as st
import streamlit_authenticator as stauth


def login() -> bool:
    """Login into app

    Returns:
        bool: The result of the login attempt, True if successful.
    """
    authenticator = _authenticator()
    authenticator.login("Login", "main")
    if st.session_state["authentication_status"]:
        authenticator.logout("Logout", "main", key="unique_key")
        _reset_password(authenticator)
        return True
    if st.session_state["authentication_status"] is False:
        st.error("Username/password is incorrect")
        return False
    if st.session_state["authentication_status"] is None:
        st.warning("Please enter your username and password")
        return False


def _reset_password(authenticator: stauth.Authenticate) -> None:
    """Resets users password after login

    Args:
        authenticator (stauth.Authenticate): The authenticator used to login.
    """
    if authenticator.reset_password(
        username=st.session_state["username"],
        form_name="Reset password",
        location="sidebar",
    ):
        st.success("Password modified successfully")
        _update_config(authenticator)


def register_user() -> None:
    """Register a new user."""
    authenticator = _authenticator()
    if authenticator.register_user("Create user", preauthorization=False):
        st.success("User registered successfully")
        _update_config(authenticator)


def _update_config(authenticator: stauth.Authenticate) -> None:
    """Update the users login details.

    Args:
        authenticator (stauth.Authenticate): The authenticator used to login.
    """
    config = {
        "credentials": authenticator.credentials,
        "cookie": {
            "expiry_days": authenticator.cookie_expiry_days,
            "key": authenticator.key,
            "name": authenticator.cookie_name,
        },
        "preauthorized": authenticator.preauthorized,
    }
    with open("selections/config.yaml", "w", encoding="utf-8") as file:
        yaml.dump(config, file, default_flow_style=False)


def _authenticator() -> stauth.Authenticate:
    """Pass the paramaters to the authenicator.

    Returns:
        stauth.Authenticate: The authenicator.
    """
    with open("selections/config.yaml", "r", encoding="utf-8") as file:
        config = yaml.load(file, Loader=SafeLoader)
    return stauth.Authenticate(
        credentials=config["credentials"],
        cookie_name=config["cookie"]["name"],
        key=config["cookie"]["key"],
        cookie_expiry_days=config["cookie"]["expiry_days"],
    )
