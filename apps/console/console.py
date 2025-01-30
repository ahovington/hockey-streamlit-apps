from typing import Optional
import streamlit as st

from config import config
from console.xero_auth import XeroOAuthToken, XeroInvoice
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
    if "code" not in st.query_params:
        return

    headers = XeroToken.request_headers(st.query_params["code"])
    st.write(headers)

    st.write(get_invoices(XeroInvoice(headers), invoice_numnber=["WEST-24-110381"]))


def get_invoices(
    invoice: XeroInvoice,
    invoice_numnber: Optional[list[str]] = None,
    statuses: Optional[list[str]] = None,
) -> list[dict]:
    filters = []
    if invoice_numnber:
        filters.append(f"InvoiceNumbers={ ','.join(invoice_numnber) }")
    if statuses:
        # TODO: This request only accepts multiple statuses
        filters.append(f"Statuses={ ','.join(statuses) }")
    for i in range(10):
        while True:
            try:
                data = invoice.get(filters=filters)["Invoices"]
            except Exception:
                continue
            break
    return data


main()
