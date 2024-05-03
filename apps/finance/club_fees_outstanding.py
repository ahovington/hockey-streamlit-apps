import streamlit as st
import datetime as dt
import pandas as pd

from utils import read_data, financial_string_formatting


def ClubFeesOustanding() -> None:
    """Summarise outstanding payments.

    Retuns: None
    """

    _, col2 = st.columns([3, 7])
    invoices = invoice_data()
    _invoices = invoices.copy()
    _invoices.loc[:, "due_date"] = pd.to_datetime(_invoices.loc[:, "due_date"])

    # Headline statistics
    st.subheader("OVERDUE CLUB FEES", divider="green")
    overdue = _invoices[_invoices["due_date"] <= dt.datetime.now()]
    col1, _, _, _ = st.columns([1, 1, 1, 1])
    col1.metric(
        "Amount due", financial_string_formatting(overdue["total_amount_due"].sum())
    )

    # Table of overdue fees
    st.write("OVERDUE INVOICES", divider="green")
    st.dataframe(overdue, hide_index=True, use_container_width=True)
    st.write("PLAYERS WITH MULTIPLE INVOICES", divider="green")
    st.dataframe(largest_over_due_debitors(), hide_index=True, use_container_width=True)

    # Table of fees due in the future
    st.subheader("UPCOMING CLUB FEES", divider="green")
    upcoming = _invoices[_invoices["due_date"] > dt.datetime.now()]
    st.write("FEES DUE IN THE NEXT MONTH")
    st.metric(
        "",
        financial_string_formatting(upcoming["total_amount_due"].sum()),
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
            r.grade,
            i.due_date,
            i.amount - (i.discount + i.amount_credited + i.amount_paid) as total_amount_due,
            i.amount as amount_invoiced,
            i.discount,
            i.amount_paid,
            i.amount_credited
        from invoices as i
        inner join registrations as r
        on i.registration_id = r.id
        inner join players as p
        on i.player_id = p.id
        where
            i.status not in ('PAID', 'VOID', 'VOIDED', 'DELETED') and
            i.due_date < (current_date + INTERVAL'1 month') and
            i.on_payment_plan = false
        order by
            r.season,
            i.due_date,
            total_amount_due desc,
            issued_date asc
    """
    )


def largest_over_due_debitors() -> pd.DataFrame:
    """Extact the outstanding club fees.

    Retuns:
        pd.DataFrame: The results of the query.
    """
    return read_data(
        f"""
        with outstanding_invoices as (
            select
                p.id as player_id,
                count(*)
            from invoices as i
            inner join players as p
            on i.player_id = p.id
            where
                i.status not in ('PAID', 'VOID', 'VOIDED', 'DELETED') and
                i.on_payment_plan = false
            group by
                p.id
            having
                count(*) > 1
        )

        select
            p.full_name,
            sum(i.amount - (i.discount + i.amount_credited + i.amount_paid)) as total_amount_due,
            sum(i.amount) as amount_invoiced,
            sum(i.discount) as discount,
            sum(i.amount_paid) as amount_paid,
            sum(i.amount_credited) as amount_credited
        from invoices as i
        inner join registrations as r
        on i.registration_id = r.id
        inner join players as p
        on i.player_id = p.id
        inner join outstanding_invoices as oi
        on i.player_id = oi.player_id
        group by
            p.full_name
        order by
            total_amount_due desc
    """
    )
