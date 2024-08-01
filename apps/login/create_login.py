import streamlit as st

from auth import register_user


def main():
    register_user()

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


main()
