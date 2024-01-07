import streamlit as st
import datetime as dt
import pandas as pd

from utils import read_data, finacial_string_formatting


def ClubFeesOustanding() -> None:
    """Summarise outstanding payments.

    Retuns: None
    """
    _, col2 = st.columns([3, 7])

    invoices = invoice_data()
    _invoices = invoices.copy()
    _invoices.loc[:, "due_date"] = pd.to_datetime(_invoices.loc[:, "due_date"])

    # Headline statistics
    st.subheader("Overdue Club Fees", divider="green")
    overdue = _invoices[_invoices["due_date"] <= dt.datetime.now()]
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    col1.metric("Net amount", finacial_string_formatting(overdue["total_amount"].sum()))
    col2.metric("Gross amount", finacial_string_formatting(overdue["amount"].sum()))
    col3.metric(
        "Discounts applied", finacial_string_formatting(overdue["discount"].sum())
    )
    col4.metric(
        "Per game adjustments applied",
        finacial_string_formatting(overdue["per_game_adjustment"].sum()),
    )

    # Table of overdue fees
    st.subheader("OVERDUE CLUB FEES", divider="green")
    st.dataframe(overdue, hide_index=True, use_container_width=True)

    # Table of fees due in the future
    st.subheader("UPCOMING CLUB FEES", divider="green")
    upcoming = _invoices[_invoices["due_date"] > dt.datetime.now()]
    st.metric(
        "Upcoming fees due", finacial_string_formatting(upcoming["total_amount"].sum())
    )
    st.dataframe(upcoming, hide_index=True, use_container_width=True)


def invoice_data() -> pd.DataFrame:
    """Extact the outstanding club fees.

    Retuns:
        pd.DataFrame: The results of the query.
    """
    return read_data(
        f"""
        select
            p.full_name,
            i.issued_date as registration_date,
            i.due_date,
            i.amount,
            i.discount,
            i.amount_paid,
            i.per_game_adjustment_applied as per_game_adjustment,
            i.amount - i.discount - i.amount_credited as total_amount,
            i.on_payment_plan
        from invoices as i
        inner join registrations as r
        on i.registration_id = r.id
        inner join players as p
        on i.player_id = p.id
        where
            i.status not in ('PAID', 'VOID') and
            i.due_date < (current_date + INTERVAL'1 month')
        order by
            r.season,
            i.due_date,
            total_amount desc,
            issued_date asc
    """
    )
