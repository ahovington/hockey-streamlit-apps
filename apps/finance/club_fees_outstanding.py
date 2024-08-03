import streamlit as st
import datetime as dt
import pandas as pd

from utils import auth_validation, financial_string_formatting
from finance.models import invoice_data, largest_over_due_debitors


@auth_validation
def main() -> None:
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

    overdue_invoices(overdue)
    upcoming_invoices(_invoices)


def overdue_invoices(df: pd.DataFrame) -> None:
    # Table of overdue fees
    st.write("OVERDUE INVOICES", divider="green")
    if not df.shape[0]:
        st.write("No overdue invoices")
        return
    _df = df.drop(["team", "team_order"], axis=1)
    st.dataframe(_df, hide_index=True, use_container_width=True)
    with st.expander("Outstanding invoices by team"):
        season = st.selectbox(
            "Season",
            df["season"].drop_duplicates(),
            index=0,
            placeholder="Select season...",
        )
        teams_table(df[(df["season"] == season) & (df["amount_paid"] == 0)])
    largest_debitors = largest_over_due_debitors()
    if not largest_debitors.shape[0]:
        return
    st.write("PLAYERS WITH MULTIPLE INVOICES", divider="green")
    st.dataframe(largest_debitors, hide_index=True, use_container_width=True)


def teams_table(df: pd.DataFrame) -> None:
    """The players with outstading fees per team.

    Args:
        df (pd.DataFrame): A dataframe with the players allocated to a team

    Retuns: None
    """
    # Calculate output table column order
    df.loc[:, "team"] = df.loc[:, "team"].fillna("Not allocated")
    df.loc[:, "selection_no"] = (df.groupby(["team"]).cumcount()) + 1
    col_order = (
        df[["team", "team_order"]]
        .drop_duplicates()
        .sort_values("team_order")["team"]
        .values
    )
    st.table(
        df.pivot(
            columns="team",
            values="full_name",
            index="selection_no",
        )[
            col_order
        ].fillna("")
    )


def upcoming_invoices(df: pd.DataFrame) -> None:
    # Table of fees due in the future
    st.subheader("UPCOMING CLUB FEES", divider="green")
    upcoming = df[df["due_date"] > dt.datetime.now()]
    if not upcoming.shape[0]:
        st.write("No upcoming invoices")
        return
    st.write("FEES DUE IN THE NEXT MONTH")
    st.metric(
        "",
        financial_string_formatting(upcoming["total_amount_due"].sum()),
    )
    st.dataframe(
        upcoming.groupby("grade").agg({"total_amount_due": ["sum", "count"]}).T,
        hide_index=False,
        use_container_width=True,
    )
    st.dataframe(upcoming, hide_index=True, use_container_width=True)


main()
