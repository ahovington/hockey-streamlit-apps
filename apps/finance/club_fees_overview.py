import pandas as pd
import streamlit as st
import altair as alt

from utils import config, read_data, financial_string_formatting


def ClubFeesOverview() -> None:
    """Summarise outstanding payments.

    Retuns: None
    """
    _, col2 = st.columns([3, 7])
    config.app.seasons.sort(reverse=True)
    season = col2.selectbox(
        "Season", config.app.seasons, index=0, placeholder="Select season..."
    )
    st.subheader("Club Fee Overview", divider="green")

    invoices = invoice_data()
    if not invoices.shape[0]:
        st.warning("No invoices found")
        return
    _invoices = invoices.copy()
    if season:
        _invoices = invoices[invoices["season"] == season]
    _invoices = _invoices.drop(columns=["season"])
    # Headline statistics
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    col1.metric(
        "Total Fees", financial_string_formatting(_invoices["amount_invoiced"].sum())
    )
    col2.metric(
        "Fees collected",
        financial_string_formatting(_invoices["amount_paid"].sum()),
    )
    col3.metric(
        "Discounts applied", financial_string_formatting(_invoices["discount"].sum())
    )
    col4.metric(
        "Credits applied",
        financial_string_formatting(_invoices["amount_credited"].sum()),
    )
    col5.metric(
        "Net amount outstanding",
        financial_string_formatting(_invoices["amount_due"].sum()),
    )

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    rego_filter = ""
    if season:
        rego_filter = f"where season = '{ season }'"
    paid_on_time = _invoices[_invoices["amount_invoiced"] > 0].drop_duplicates(
        subset=["registration_id"]
    )
    col1.metric("Players invoiced", _invoices["registration_id"].nunique())
    col2.metric(
        "Paid",
        f"""
            { paid_on_time[-paid_on_time['fully_paid_date'].isna()].shape[0] / paid_on_time.shape[0] :.1%}
        """,
    )
    col3.metric(
        "Paid on time",
        f"""
            { paid_on_time["paid_early"].sum() / paid_on_time.shape[0] :.1%}
        """,
    )
    col4.metric(
        "Average fee collected",
        financial_string_formatting(
            _invoices["amount_paid"].sum() / _invoices["registration_id"].nunique()
        ),
    )

    # Timeseries of collected fees
    st.subheader("Fees fully paid by month", divider="green")
    collected_fees = _invoices[~_invoices["fully_paid_month"].isna()]
    if collected_fees.shape[0]:
        collected_fees = (
            collected_fees.groupby("fully_paid_month")
            .agg({"amount_paid": "sum"})
            .reset_index()
        )
        get_line_chart(
            collected_fees,
            date_col="fully_paid_month",
            y_col="amount_paid",
        )
    else:
        st.warning("No payments have been received for this period.")

    distinct_regos = _invoices.drop_duplicates(subset=["registration_id"])
    distinct_regos.loc[:, "invoice_description"] = (
        distinct_regos.loc[:, "invoice_description"]
        .str.lower()
        .str.replace("instalment 1 of west hockey club fees", "paid by instalments")
        .str.replace("instalment 5 of west hockey club fees", "paid by instalments")
        .str.replace("1st instalment", "paid by instalments")
    )
    # player types
    st.subheader("Invoices by player type", divider="green")
    player_types = (
        distinct_regos.groupby(["invoice_description"])
        .agg({"id": "count"})
        .reset_index()
    )
    player_types.columns = ["fee type", "registration count"]
    get_bar_chart(
        player_types,
        "fee type",
        "registration count",
    )

    # discounts taken up
    st.subheader("Invoices by discount type", divider="green")
    collection_method = (
        distinct_regos.groupby(["discount_applied"]).agg({"id": "count"}).reset_index()
    )
    collection_method.columns = ["discount applied", "registration count"]
    get_bar_chart(collection_method, "discount applied", "registration count")

    st.subheader("Detailed invoice table", divider="green")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    invoice_status = col1.selectbox(
        "Status",
        _invoices["status"].unique().tolist(),
        index=None,
        placeholder="Select status...",
    )
    invoice_type = col2.selectbox(
        "Invoice type",
        _invoices["invoice_description"].unique().tolist(),
        index=None,
        placeholder="Select invoice type...",
    )
    if invoice_status:
        _invoices = _invoices[_invoices["status"] == invoice_status]
    if invoice_type:
        _invoices = _invoices[_invoices["invoice_description"] == invoice_type]
    st.write(_invoices)


def invoice_data() -> pd.DataFrame:
    """Extact the outstanding club fees.

    Retuns:
        pd.DataFrame: The results of the query.
    """
    df = read_data(
        f"""
        select
            i.id,
            p.full_name,
            r.season,
            r.id as registration_id,
            i.status,
            i.issued_date as registration_date,
            i.due_date,
            i.invoice_sent,
            i.on_payment_plan,
            i.discount_applied,
            i.fully_paid_date,
            date_trunc('MONTH', i.fully_paid_date) as fully_paid_month,
            i.amount - (i.discount + i.amount_credited + i.amount_paid) as amount_due,
            i.amount as amount_invoiced,
            i.discount,
            i.amount_paid as amount_paid,
            i.amount_credited,
            i.lines
        from invoices as i
        inner join registrations as r
        on i.registration_id = r.id
        inner join players as p
        on i.player_id = p.id
        where
            i.status not in ('VOID', 'VOIDED', 'DELETED')
        order by
            r.season,
            i.due_date,
            i.create_ts desc,
            amount_due desc,
            issued_date asc
    """
    )
    df.loc[:, "invoice_description"] = df["lines"].str[0].str["Description"]
    date_cols = ["due_date", "fully_paid_date", "fully_paid_month"]
    for date_col in date_cols:
        df.loc[:, date_col] = pd.to_datetime(df.loc[:, date_col], errors="coerce")
    df.loc[:, "paid_early"] = (df["due_date"] >= df["fully_paid_date"]) | df[
        "on_payment_plan"
    ]
    df = df.drop(columns=["lines"])
    return df


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
