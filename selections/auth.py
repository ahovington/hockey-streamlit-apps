import yaml
from yaml.loader import SafeLoader
import streamlit as st
import streamlit_authenticator as stauth

# st.write(stauth.Hasher(["admin"]).generate())

with open("selections/config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)


def login_page() -> bool:
    authenticator = stauth.Authenticate(
        config["credentials"], config["cookie"]["name"], config["cookie"]["key"]
    )

    name, authentication_status, username = authenticator.login("Login", "main")

    if authentication_status:
        authenticator.logout("Logout", "main")
        st.write(f"Welcome *{name}*")
        return True
    elif authentication_status == False:
        st.error("Username/password is incorrect")
        return False
    elif authentication_status == None:
        st.warning("Please enter your username and password")
        return False
