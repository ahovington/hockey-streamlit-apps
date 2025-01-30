import streamlit as st

from config import config
from console.xero_auth import XeroOAuthToken
from utils import auth_validation

TENANT = "West Hockey Club"
XeroToken = XeroOAuthToken(config, TENANT)


@auth_validation
def main() -> None:
    """Refresh data between revolutionise, Xero and the database."""
    st.title("UNDER DEVELOPMENT: West Hockey Invoicing Console")
    st.subheader("Refresh registrations", divider="green")
    st.write("To be implemented")
    st.subheader("Invoicing", divider="green")
    st.link_button(
        label="Auth",
        url=XeroToken.oauth_url,
        use_container_width=True,
    )

    st.write(st.query_params)
    if "code" in st.query_params:
        st.write(XeroToken.request_headers(st.query_params["code"]))


main()
