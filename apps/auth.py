import hashlib
import streamlit as st
import streamlit_authenticator as stauth

from utils import read_data, update_data


def login(authenticator: stauth.Authenticate) -> bool:
    """Login into app

    Returns:
        bool: The result of the login attempt, True if successful.
    """
    authenticator.login("Login", "main")
    try:
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
    except TypeError:
        st.session_state["authentication_status"] = False
        authenticator.logout("Logout", "main", key="unique_key")


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


def register_user(authenticator: stauth.Authenticate) -> None:
    """Register a new user."""
    st.write(
        "You can only create a login if you have been added to a pre-approved list of users."
    )
    st.write("Example inputs")
    st.dataframe(
        {
            "email": "Email you registered with",
            "username": "example",
            "name": "example",
            "password": "dont reuse a password!",
            "Repeat password": "dont reuse a password!",
        }
    )
    if authenticator.register_user("", preauthorization=True):
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
                    "password": row.get("hashed_password", ""),
                }
                for _, row in users.iterrows()
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
        cookie_expiry_days=1,
        preauthorized=config.get("preauthorized", []),
    )
