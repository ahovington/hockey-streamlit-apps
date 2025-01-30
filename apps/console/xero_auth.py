import base64
from typing import List, Dict, Optional
import json
import logging
import requests
from requests.adapters import HTTPAdapter, Retry
import certifi

from config import Config

import streamlit as st

XERO_API_URL = "https://api.xero.com/api.xro/2.0/"
REQUEST_TIMEOUT = 30


def make_request(
    method: str,
    endpoint: str,
    headers: dict = None,
    data: dict = None,
    return_json: bool = True,
) -> dict:
    try:
        s = requests.Session()
        retries = Retry(
            total=1,
            backoff_factor=1.0,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "PUT", "POST"],
        )
        s.mount("https://", HTTPAdapter(max_retries=retries))
        request = {
            "method": method.upper(),
            "url": endpoint,
            "timeout": REQUEST_TIMEOUT,
            "verify": certifi.where(),
        }
        if headers:
            request["headers"] = headers
        if data:
            request["data"] = json.dumps(data)
        r = s.request(**request)
        if not r.ok:
            raise Exception(f"Endpoint {endpoint} returned with error {r}: {r.reason}")
        if return_json:
            return r.json()
        return r.text
    finally:
        s.close()


class XeroOAuthToken:

    AUTHORIZATION_ENDPOINT = "https://login.xero.com/identity/connect/authorize?"
    TOKEN_ENDPOINT = "https://identity.xero.com/connect/token"
    REDIRECT_URI = "https://west-hockey-newcastle.onrender.com/"
    SCOPES = [
        "openid",
        "profile",
        "email",
    ]
    CONNECTIONS_ENDPOINT = "https://api.xero.com/connections"

    def __init__(self, config: Config, tenant_name: str) -> None:
        self.config = config
        self.tenant_name = tenant_name

    @property
    def oauth_url(self) -> str:
        payload = {
            "response_type": "code",
            "client_id": self.config.xero.client_id,
            "redirect_uri": XeroOAuthToken.REDIRECT_URI,
            "scope": " ".join(XeroOAuthToken.SCOPES),
        }
        url = f"{XeroOAuthToken.AUTHORIZATION_ENDPOINT}response_type={payload['response_type']}&client_id={payload['client_id']}&redirect_uri={payload['redirect_uri']}&scope={payload['scope']}"
        return url

    def request_headers(self, auth_code: str):
        self.token = self._get_access_token(auth_code)
        self.tenant_id = self._get_tenant_id(self.token)
        return {
            "Authorization": f"Bearer {self.token}",
            "Xero-tenant-id": self.tenant_id,
            "Accept": "application/json",
        }

    def _get_access_token(self, auth_code: str) -> str:
        """
        Take authentication code and return access token.
        """
        credentials = self.config.xero.client_id + ":" + self.config.xero.client_secret
        data = {
            "authorization": "Basic "
            + base64.b64encode(credentials.encode("utf-8")).decode("utf-8"),
            "Content-Type": "application/x-www-form-urlencoded",
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": XeroOAuthToken.REDIRECT_URI,
        }

        st.write(data)

        # r = requests.post(
        #     XeroOAuthToken.TOKEN_ENDPOINT,
        #     data=data,
        #     verify=certifi.where(),
        # )
        r = requests.post(
            f"""https://identity.xero.com/connect/token authorization: Basic {data["authorization"]} Content-Type: application/x-www-form-urlencoded grant_type=authorization_code&code={auth_code}&redirect_uri={data["redirect_uri"]}""",
            verify=certifi.where(),
        )
        if not r.ok:
            raise Exception(
                f"Retrieving the access token returned with error {r}: {r.reason}"
            )
        st.write(r.json())
        # return r.json()["access_token"]

    def _get_tenant_id(self, token: str) -> str:
        tenants = requests.get(
            XeroOAuthToken.CONNECTIONS_ENDPOINT,
            headers={"Authorization": f"Bearer { token }"},
            verify=certifi.where(),
        ).json()
        for tenant in tenants:
            if (
                self.tenant_name.upper() == tenant["tenantName"].upper()
                and tenant["tenantType"] == "ORGANISATION"
            ):
                return tenant["tenantId"]
        return logging.error(
            f"Tenant {self.tenant_name} not found, available tenants are {[t['tenantName'] for t in tenants]}"
        )


class XeroCreditNote:
    BASE_ENDPOINT = XERO_API_URL + "CreditNotes"

    def __init__(self, xero_oauth_token: XeroOAuthToken) -> None:
        self.headers = xero_oauth_token.request_headers()

    def get(
        self,
        filters: Optional[List[str]] = None,
    ) -> dict:
        endpoint = XeroCreditNote.BASE_ENDPOINT + "?"
        if filters:
            endpoint += "&".join(filters)
        return make_request("GET", endpoint, self.headers)

    def put(
        self,
        contact_id: str,
        credit_note_number: str,
        credit_note_date: str,
        line_item_description: str,
        line_item_quantity: float,
        line_item_unit_amount: float,
        line_item_account_code: str,
        reference: str = None,
        credit_note_status: str = "AUTHORISED",
        credit_note_type: str = "ACCRECCREDIT",
        Line_amount_types: str = "NoTax",
        currency_code: str = "AUD",
    ) -> dict:
        data = {
            "Type": credit_note_type,
            "CreditNoteNumber": credit_note_number,
            "Contact": {"ContactID": contact_id},
            "Date": credit_note_date,
            "Reference": reference,
            "LineAmountTypes": Line_amount_types,
            "LineItems": [
                {
                    "Description": line_item_description,
                    "Quantity": line_item_quantity,
                    "UnitAmount": line_item_unit_amount,
                    "AccountCode": line_item_account_code,
                }
            ],
            "Status": credit_note_status.upper(),
            "CurrencyCode": currency_code,
        }
        return make_request("PUT", XeroCreditNote.BASE_ENDPOINT, self.headers, data)

    def post(self, invoice_number: str, amount: float) -> dict:
        endpoint = XeroCreditNote.BASE_ENDPOINT + f"/{invoice_number}"
        data = {"Invoice": invoice_number, "Amount": amount}
        return make_request("POST", endpoint, self.headers, data)


class XeroInvoice:
    BASE_ENDPOINT = XERO_API_URL + "Invoices"

    def __init__(self, xero_oauth_headers: dict) -> None:
        self.headers = xero_oauth_headers

    def get(
        self, filters: Optional[list[str]] = None, resource: Optional[list[str]] = None
    ) -> dict:
        endpoint = XeroInvoice.BASE_ENDPOINT
        if filters:
            endpoint += "?"
            endpoint += "&".join(filters)
        if resource:
            endpoint += "/"
            endpoint += resource
        return make_request("GET", endpoint, self.headers)

    def put(
        self,
        contact_id: str,
        invoice_date: str,
        due_date: str,
        invoice_status: str,
        line_items: List[Dict[str, str]],
        invoice_numnber: str = None,
        reference: str = None,
        invoice_type: str = "ACCREC",
        branding_theme: str = "14b85e01-39be-45e3-ba84-9dcd59dec56d",  # go cardless theme
        currency_code: str = "AUD",
    ) -> dict:
        data = {
            "InvoiceNumber": invoice_numnber,
            "Type": invoice_type,
            "Contact": {"ContactID": contact_id},
            "DateString": invoice_date,
            "DueDateString": due_date,
            "Reference": reference,
            "BrandingThemeID": branding_theme,
            "CurrencyCode": currency_code,
            "Status": invoice_status.upper(),
            "LineItems": line_items,
        }
        return make_request("PUT", XeroInvoice.BASE_ENDPOINT, self.headers, data)

    def post(self, invoice_number: str, **kwargs) -> dict:
        endpoint = f"{ XeroInvoice.BASE_ENDPOINT }/{ invoice_number }"
        data = {"InvoiceNumber": invoice_number, **kwargs}
        return make_request("POST", endpoint, self.headers, data)

    def send_invoice(self, invoice_id: str) -> None:
        send_email = f"{ XeroInvoice.BASE_ENDPOINT }/{ invoice_id }/Email"
        return make_request("POST", send_email, self.headers, return_json=False)


class XeroContact:
    BASE_ENDPOINT = XERO_API_URL + "Contacts"

    def __init__(self, xero_oauth_token: XeroOAuthToken) -> None:
        self.headers = xero_oauth_token.request_headers()

    def get(
        self, account_number: Optional[str] = None, filters: Optional[str] = None
    ) -> dict:
        endpoint = XeroContact.BASE_ENDPOINT + "?"  # + "?summaryOnly=True"
        if account_number:
            endpoint += f'&where=AccountNumber="{account_number}"'
        if filters:
            endpoint += filters
        return make_request("GET", endpoint, self.headers)

    def put(
        self,
        full_name: str,
        first_name: str,
        last_name: str,
        email_address: str,
        mobile_number: str,
        registration_number: str,
    ) -> dict:
        data = {
            "Name": full_name,
            "FirstName": first_name,
            "LastName": last_name,
            "EmailAddress": email_address,
            "Phones": [{"PhoneType": "MOBILE", "PhoneNumber": mobile_number}],
            "AccountNumber": registration_number,
        }
        return make_request("PUT", XeroContact.BASE_ENDPOINT, self.headers, data)

    def post(
        self,
        contact_id: str,
        full_name: str,
        first_name: str,
        last_name: str,
        email_address: str,
        mobile_number: str,
        registration_number: str,
    ) -> dict:
        # TODO: Make this generic like the invoice post method.
        data = {
            "ContactID": contact_id,
            "Name": full_name,
            "FirstName": first_name,
            "LastName": last_name,
            "EmailAddress": email_address,
            "Phones": [{"PhoneType": "MOBILE", "PhoneNumber": mobile_number}],
            "AccountNumber": registration_number,
        }
        return make_request("POST", XeroContact.BASE_ENDPOINT, self.headers, data)


# TODO: For maintaince of direct debit payers, add them to a direct debit group.
class XeroContactGroup:
    BASE_ENDPOINT = f"{XERO_API_URL}ContactGroups"

    def __init__(self, xero_oauth_token: XeroOAuthToken) -> None:
        self.headers = xero_oauth_token.request_headers()

    def get(
        self, contact_group_id: Optional[str] = None, filters: Optional[str] = None
    ) -> dict:
        endpoint = XeroContact.BASE_ENDPOINT
        if contact_group_id:
            endpoint += f'/"{contact_group_id}"'
        if filters:
            endpoint += filters
        return make_request("GET", endpoint, self.headers)

    def put(self, contact_group_id: str, contact_ids: List[str]) -> dict:
        endpoint = f"{XeroContact.BASE_ENDPOINT}/{contact_group_id}/Contacts"
        data = {"Contacts": [{"ContactID": contact_id} for contact_id in contact_ids]}
        return make_request("PUT", endpoint, self.headers, data)

    def post(self) -> dict:
        pass
