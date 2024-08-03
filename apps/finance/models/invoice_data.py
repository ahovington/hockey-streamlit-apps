import pandas as pd

from utils import read_data


def invoice_data() -> pd.DataFrame:
    """Extact the outstanding club fees.

    Retuns:
        pd.DataFrame: The results of the query.
    """
    return read_data(
        f"""
        select
            r.season,
            p.full_name,
            r.grade,
            i.due_date,
            i.amount - (i.discount + i.amount_credited + i.amount_paid) as total_amount_due,
            i.amount as amount_invoiced,
            i.discount,
            i.amount_paid,
            i.amount_credited,
            r.team,
            t.team_order
        from invoices as i
        inner join registrations as r
        on i.registration_id = r.id
        inner join players as p
        on i.player_id = p.id
        left join teams as t
        on t.id = r.team_id
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


def invoice_overview_data() -> pd.DataFrame:
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
                r.grade,
                i.due_date,
                i.invoice_sent,
                i.on_payment_plan,
                i.discount_applied,
                i.fully_paid_date,
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
                    else (pp.amount_paid / (pp.amount_invoiced - (pp.discount + pp.amount_credited)) * 100)::text || '%% PAID'
                end as status,
                i.registration_date,
                i.grade,
                pp.due_date,
                pp.invoice_sent,
                pp.on_payment_plan,
                pp.discount_applied,
                pp.fully_paid_date,
                pp.amount_due,
                pp.amount_invoiced,
                pp.discount,
                pp.amount_paid,
                pp.amount_credited,
                i.lines
            from _invoices as i
            inner join agg_payment_plan as pp
            on i.id = pp.id
        ),

        combine as (
            select *
            from _invoices
            where
                status not in ('VOID', 'VOIDED', 'DELETED') and
                on_payment_plan = false

            union all

            select *
            from join_orig_invoice
        )

        select
            id,
            create_ts,
            full_name,
            season,
            registration_id,
            case
                when status = 'PAID' then status
                when on_payment_plan then status
                when amount_due > 0 and amount_paid > 0 then 'PARTIALLY PAID'
                else status
            end as status,
            registration_date,
            grade,
            due_date,
            invoice_sent,
            on_payment_plan,
            discount_applied,
            fully_paid_date,
            amount_due,
            amount_invoiced,
            discount,
            amount_paid,
            amount_credited,
            lines
        from combine
        order by
            season,
            due_date,
            registration_date desc,
            amount_due desc
    """
    )
    df.loc[:, "invoice_description"] = df["lines"].str[0].str["Description"]
    df = df[df["invoice_description"] != "Non paying player"]
    date_cols = ["due_date", "fully_paid_date"]
    for date_col in date_cols:
        df.loc[:, date_col] = pd.to_datetime(df.loc[:, date_col], errors="coerce")
    df.loc[:, "paid_early"] = (df["due_date"] >= df["fully_paid_date"]) | df[
        "on_payment_plan"
    ]
    df = df.drop(columns=["lines"])
    return df


def collected_fees_data(season: str) -> pd.DataFrame:
    """Show the cummulative fees collected for the season

    Args:
        season (str): The season to show the chart for.
    """
    return read_data(
        f"""
            select
                i.id,
                i.fully_paid_date,
                date_trunc('WEEK', i.fully_paid_date) as fully_paid_week,
                i.amount_paid
            from invoices as i
            inner join registrations as r
            on i.registration_id = r.id
            where
                i.status not in ('VOID', 'VOIDED', 'DELETED') and
                r.season = '{season}'
        """
    )
