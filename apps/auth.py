import hashlib
import streamlit as st
import streamlit_authenticator as stauth

from config import config
from utils import read_data, update_data


def auth(roles: list[str]) -> stauth.Authenticate:
    """Pass the paramaters to the authenicator.

    Args:
        roles list[str]: List of roles that are allowed access to the application.

    Returns:
        stauth.Authenticate: The authenicator.
    """
    users = read_data(
        f"""
        select
            id,
            name,
            username,
            email,
            hashed_password
        from users
        where
            role in (
                '{ "', '".join(roles) }'
            )
        """
    )
    config = {
        "credentials": {
            "usernames": {
                row["email"]: {
                    "id": row["id"],
                    "email": row["email"],
                    "name": row["name"],
                    "password": row["hashed_password"],
                }
                for _, row in users[~users["hashed_password"].isna()].iterrows()
            }
        },
        "preauthorized": {
            "emails": [
                email for email in users[users["hashed_password"].isna()]["email"]
            ]
        },
    }
    return stauth.Authenticate(
        credentials=config["credentials"],
        cookie_name="selections_streamlit_cookie",
        key="west-hockey-newcastle",
        cookie_expiry_days=30,
        preauthorized=config.get("preauthorized", []),
    )


AUTHENTICATOR = auth(config.app.user_groups)


def login(authenticator: stauth.Authenticate = AUTHENTICATOR):
    """Login into app"""
    # initalise session state variables
    st.session_state["authentication_status"] = False
    st.session_state["username"] = None
    st.session_state["name"] = None
    st.session_state["logout"] = False
    _, logged_in, username = authenticator.login(form_name="Login", location="main")
    if username and not logged_in and not st.session_state["authentication_status"]:
        st.error("Username/password is incorrect")


def logout(authenicator: stauth.Authenticate = AUTHENTICATOR):
    """Log out of the app"""
    authenicator.logout(button_name="Logout", location="sidebar", key="unique_key")


def reset_password(authenticator: stauth.Authenticate = AUTHENTICATOR) -> None:
    """Resets users password after login

    Args:
        authenticator (stauth.Authenticate): The authenticator used to login.
    """
    if authenticator.reset_password(
        form_name="Reset password",
        username=st.session_state["username"],
        location="main",
    ):
        st.success("Password modified successfully")
        _update_config(authenticator)


def register_user(authenticator: stauth.Authenticate = AUTHENTICATOR) -> None:
    """Register a new user."""
    st.write(
        "You can only create a login if you have been added to a pre-approved list of users."
    )
    if authenticator.register_user(
        form_name="",
        location="main",
        preauthorization=True,
        # TODO: will probably need to add this back in a day.
        # fields={
        #     "Email": "Email",
        #     "Username": "Username",
        #     "Password": "Password",
        #     "Repeat password": "Repeat password",
        #     "Register": "Register",
        # },
    ):
        st.success("User registered successfully")
        _update_config(authenticator)


def _update_config(authenticator: stauth.Authenticate) -> None:
    """Update the users login details.

    Args:
        authenticator (stauth.Authenticate): The authenticator used to login.
    """
    gen_id = lambda x: hashlib.shake_256(x.encode("utf-8")).hexdigest(20)
    for username, attrs in authenticator.credentials["usernames"].items():
        if not attrs["password"]:
            continue
        update_data(
            "users",
            column="hashed_password",
            value=attrs["password"],
            row_id=gen_id(attrs["email"]),
            value_string_type=True,
        )
        update_data(
            "users",
            column="username",
            value=username,
            row_id=gen_id(attrs["email"]),
            value_string_type=True,
        )
