from typing import Any
import pandas as pd
import streamlit as st
import altair as alt

from config import config
from utils import (
    auth_validation,
    financial_string_formatting,
)
from finance.models import collected_fees_data, invoice_overview_data


@auth_validation
def main() -> None:
    """Summarise outstanding payments.

    Retuns: None
    """
    _, col2 = st.columns([3, 7])
    config.app.seasons.sort(reverse=True)
    season = col2.selectbox(
        "Season", config.app.seasons, index=0, placeholder="Select season..."
    )
    if not season:
        st.warning("Select a season from the drop down menu")
        return

    invoices = invoice_overview_data()
    if not invoices.shape[0]:
        st.warning("No invoices found")
        return

    _invoices = invoices.copy()
    _invoices = invoices[invoices["season"] == season]
    _invoices = _invoices.drop(columns=["season"])

    # check for uniqueness, one rego = one invoice
    if (
        not _invoices.drop_duplicates(subset=["registration_id"]).shape[0]
        == _invoices.shape[0]
    ):
        raise ValueError("Data contains duplicates.")

    # Show the headline invoice statistics
    headline_statistics(_invoices)

    # Timeseries of collected fees
    cummulative_fees_collected_line_chart(season)

    # Bar chart by player type
    player_type_bar_chart(_invoices)

    # Show table of all registrations
    invoice_table(_invoices)


def headline_statistics(df: pd.DataFrame):
    """Show the headline invoice statistics

    Args:
        df (pd.DataFrame): The dataframe with the invoice data
    """

    # remove zero sum invoices
    _df = df[df["amount_invoiced"] > 0]

    ## Hero metrics
    st.subheader("Club Fee Overview", divider="green")
    # First row
    hero_metrics(_df)


def cummulative_fees_collected_line_chart(season: str) -> None:
    """Show the cummulative fees collected for the season

    Args:
        season (str): The season to show the chart for.
    """
    collected_fees = collected_fees_data(season)
    st.subheader("Cummulative fully paid invoices", divider="green")
    if collected_fees.shape[0]:
        collected_fees = (
            collected_fees.groupby("fully_paid_week")
            .agg({"amount_paid": "sum"})
            .reset_index()
        )
        collected_fees["cummulative_amount"] = collected_fees["amount_paid"].cumsum()
        get_line_chart(
            collected_fees,
            date_col="fully_paid_week",
            y_col="cummulative_amount",
        )
    else:
        st.warning("No payments have been received for this period.")


def player_type_bar_chart(df: pd.DataFrame):
    _df = df.copy()
    _df.loc[:, "invoice_description"] = (
        _df.loc[:, "invoice_description"]
        .str.lower()
        .str.replace("instalment 1 of west hockey club fees", "paid by instalments")
        .str.replace("instalment 5 of west hockey club fees", "paid by instalments")
        .str.replace("1st instalment", "paid by instalments")
    )
    # player types
    st.subheader("Invoices by player type", divider="green")
    player_types = (
        _df.groupby(["invoice_description"]).agg({"id": "count"}).reset_index()
    )
    player_types.columns = ["fee type", "registration count"]
    get_bar_chart(
        player_types,
        "fee type",
        "registration count",
    )


def invoice_table(df: pd.DataFrame):
    COLUMN_ORDER = [
        "id",
        "full_name",
        "registration_id",
        "registration_date",
        "grade",
        "due_date",
        "fully_paid_date",
        "status",
        "invoice_description",
        "invoice_sent",
        "discount_applied",
        "on_payment_plan",
        "paid_early",
        "amount_due",
        "amount_invoiced",
        "discount",
        "amount_paid",
        "amount_credited",
    ]

    st.subheader("Detailed invoice table", divider="green")

    # Table filters
    col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
    invoice_status = col1.selectbox(
        "Status",
        df["status"].unique().tolist(),
        index=None,
        placeholder="Select status...",
    )
    grade = col2.selectbox(
        "Grade",
        df["grade"].unique().tolist(),
        index=None,
        placeholder="Select grade...",
    )
    invoice_type = col3.selectbox(
        "Invoice type",
        df["invoice_description"].unique().tolist(),
        index=None,
        placeholder="Select invoice type...",
    )
    col41, col42, col43, col44 = col4.columns([1, 1, 1, 1])
    invoice_sent = col41.selectbox(
        "Invoice sent",
        [True, False],
        index=None,
        placeholder="Select option",
    )
    discount_applied = col42.selectbox(
        "Discount applied",
        [True, False],
        index=None,
        placeholder="Select option",
    )
    on_payment_plan = col43.selectbox(
        "On payment plan",
        [True, False],
        index=None,
        placeholder="Select option",
    )
    paid_early = col44.selectbox(
        "Paid early",
        [True, False],
        index=None,
        placeholder="Select option",
    )

    # remove zero sum invoices
    _df = df[df["amount_invoiced"] > 0]
    # Apply filters and show table
    _df = _df[COLUMN_ORDER].copy()

    _df = apply_filters(
        _df,
        {
            "status": invoice_status,
            "invoice_description": invoice_type,
            "invoice_sent": invoice_sent,
            "discount_applied": discount_applied,
            "on_payment_plan": on_payment_plan,
            "paid_early": paid_early,
            "grade": grade,
        },
    )

    if not _df.shape[0]:
        st.error("No invoices to show")
        return

    with st.expander("Hero metrics"):
        hero_metrics(_df)

    st.write(_df)


def hero_metrics(df: pd.DataFrame):
    _df = df.copy()
    # Hero metrics
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    col1.metric("Total Fees", financial_string_formatting(_df["amount_invoiced"].sum()))
    col2.metric(
        "Net amount outstanding",
        financial_string_formatting(_df["amount_due"].sum()),
    )
    col3.metric(
        "Fees collected",
        financial_string_formatting(_df["amount_paid"].sum()),
    )
    col4.metric("Discounts", financial_string_formatting(_df["discount"].sum()))
    col5.metric(
        "Credits / Sponsorships",
        financial_string_formatting(_df["amount_credited"].sum()),
    )

    # Second row
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    col1.metric("Players invoiced", _df.shape[0])
    col2.metric(
        "Players paid",
        _df[_df["status"] == "PAID"].shape[0],
    )
    col3.metric(
        "Invoices paid",
        f"""
            { _df[_df["status"] == "PAID"].shape[0] / _df.shape[0] :.1%}
        """,
    )
    col4.metric(
        "Invoices paid on time",
        f"""
            { _df["paid_early"].sum() / _df.shape[0] :.1%}
        """,
    )
    col5.metric(
        "Average fee collected",
        financial_string_formatting(
            _df["amount_paid"].sum() / _df["registration_id"].nunique()
        ),
    )


# Define the base time-series chart.
def get_line_chart(
    data: pd.DataFrame, date_col: str, y_col: str, use_container_width: bool = True
):
    hover = alt.selection_single(
        fields=[date_col],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data)
        .mark_line(color="green")
        .encode(
            x=date_col,
            y=y_col,
        )
    )

    # Draw points on the line, and highlight based on selection
    points = lines.transform_filter(hover).mark_circle(size=65)

    # Draw a rule at the location of the selection
    tooltips = (
        alt.Chart(data)
        .mark_rule()
        .encode(
            x=date_col,
            y=y_col,
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip(date_col, title="Date"),
                alt.Tooltip(y_col, title="Price (AUD)"),
            ],
        )
        .add_params(hover)
    )
    st.altair_chart(
        (lines + points + tooltips).interactive(),
        use_container_width=use_container_width,
    )


def get_bar_chart(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    use_container_width: bool = True,
):
    chart = (
        alt.Chart(data)
        .mark_bar(color="green")
        .encode(x=alt.X(x_col).sort("-y"), y=y_col)
    )
    st.altair_chart(chart, use_container_width=use_container_width)


def apply_filters(df: pd.DataFrame, columns_to_filter: dict[str, Any]) -> pd.DataFrame:
    _df = df.copy()
    for column, filter in columns_to_filter.items():
        if filter != None:
            _df = _df[_df[column] == filter]
    return _df


main()
