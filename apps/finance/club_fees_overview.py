import pandas as pd
import streamlit as st
import altair as alt

from utils import config, read_data, financial_string_formatting, clean_query_params


def ClubFeesOverview() -> None:
    """Summarise outstanding payments.

    Retuns: None
    """
    clean_query_params(["Application", "Page"])
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
        "Net amount outstanding",
        financial_string_formatting(_invoices["amount_due"].sum()),
    )
    col3.metric(
        "Fees collected",
        financial_string_formatting(_invoices["amount_paid"].sum()),
    )
    col4.metric("Discounts", financial_string_formatting(_invoices["discount"].sum()))
    col5.metric(
        "Credits / Sponsorships",
        financial_string_formatting(_invoices["amount_credited"].sum()),
    )

    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    paid_on_time = _invoices[_invoices["amount_invoiced"] > 0].drop_duplicates(
        subset=["registration_id"]
    )
    col1.metric("Players invoiced", paid_on_time.shape[0])
    col2.metric(
        "Players paid",
        paid_on_time[paid_on_time["status"] == "PAID"].shape[0],
    )
    col3.metric(
        "Invoices paid",
        f"""
            { paid_on_time[paid_on_time["status"] == "PAID"].shape[0] / paid_on_time.shape[0] :.1%}
        """,
    )
    col4.metric(
        "Invoices paid on time",
        f"""
            { paid_on_time["paid_early"].sum() / paid_on_time.shape[0] :.1%}
        """,
    )
    col5.metric(
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
    # st.subheader("Invoices by discount type", divider="green")
    # collection_method = (
    #     distinct_regos.groupby(["discount_applied"]).agg({"id": "count"}).reset_index()
    # )
    # collection_method.columns = ["discount applied", "registration count"]
    # get_bar_chart(collection_method, "discount applied", "registration count")

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
    payment_plain = col3.selectbox(
        "Payment plan",
        [True, False],
        index=None,
        placeholder="Select option",
    )
    if invoice_status:
        _invoices = _invoices[_invoices["status"] == invoice_status]
    if invoice_type:
        _invoices = _invoices[_invoices["invoice_description"] == invoice_type]
    if payment_plain != None:
        _invoices = _invoices[_invoices["on_payment_plan"] == payment_plain]
    st.write(_invoices)


def invoice_data() -> pd.DataFrame:
    """Extact the outstanding club fees.

    Retuns:
        pd.DataFrame: The results of the query.
    """
    df = read_data(
        """
        with _invoices as (
            select
                i.id,
                r.create_ts,
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
                i.amount_paid,
                i.amount_credited,
                i.lines
            from invoices as i
            inner join registrations as r
            on i.registration_id = r.id
            inner join players as p
            on i.player_id = p.id
        ),

        agg_payment_plan as (
            select
                substring(id, 0, 15) as id,
                on_payment_plan,
                max(due_date) as due_date,
                min(invoice_sent::int)::boolean as invoice_sent,
                min(discount_applied::int)::boolean as discount_applied,
                max(fully_paid_date) as fully_paid_date,
                max(fully_paid_month) as fully_paid_month,
                sum(amount_due) as amount_due,
                sum(amount_invoiced) as amount_invoiced,
                sum(discount) as discount,
                sum(amount_paid) as amount_paid,
                sum(amount_credited) amount_credited
            from _invoices
            where
                status not in ('VOID', 'VOIDED', 'DELETED') and
                on_payment_plan = true
            group by
                substring(id, 0, 15),
                on_payment_plan
        ),

        join_orig_invoice as (
            select
                i.id,
                i.create_ts,
                i.full_name,
                i.season,
                i.registration_id,
                case
                    when pp.amount_due <= 0 then 'PAID'
                    else (pp.amount_paid / (pp.amount_invoiced - (pp.discount + pp.amount_credited)) * 100)::text || '%% Paid'
                end as status,
                i.registration_date,
                pp.due_date,
                pp.invoice_sent,
                pp.on_payment_plan,
                pp.discount_applied,
                pp.fully_paid_date,
                pp.fully_paid_month,
                pp.amount_due,
                pp.amount_invoiced,
                pp.discount,
                pp.amount_paid,
                pp.amount_credited,
                i.lines
            from _invoices as i
            inner join agg_payment_plan as pp
            on i.id = pp.id
        )

        select *
        from _invoices
        where
            status not in ('VOID', 'VOIDED', 'DELETED') and
            on_payment_plan = false

        union all

        select *
        from join_orig_invoice

        order by
            season,
            due_date,
            create_ts desc,
            amount_due desc
    """
    )
    df.loc[:, "invoice_description"] = df["lines"].str[0].str["Description"]
    df = df[df["invoice_description"] != "Non paying player"]
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
