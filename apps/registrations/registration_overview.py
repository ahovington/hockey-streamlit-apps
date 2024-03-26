import streamlit as st
import pandas as pd
import altair as alt

from utils import read_data


def RegistrationOverview(*args) -> None:
    rego_counts = registration_count()
    rego_dates = registration_dates()

    # registration count
    get_bar_chart(
        rego_counts,
        "season",
        "total_registrations",
        use_container_width=True,
    )

    # Average days players registered pre season
    avg_days_pre_season = (
        rego_dates.groupby("season")
        .agg({"days_before_first_game": "mean"})
        .reset_index()
    )
    avg_days_pre_season.loc[:, "days_before_first_game"] = abs(
        avg_days_pre_season.loc[:, "days_before_first_game"]
    )
    get_bar_chart(
        avg_days_pre_season,
        "season",
        "days_before_first_game",
        use_container_width=True,
    )

    # registrations pre season curve
    pre_season_rego_curve = rego_curve_data(rego_dates, rego_counts)
    get_line_chart(
        pre_season_rego_curve,
        "days_before_first_game",
        "cummlative_registrations_percent",
        "season",
    )


def rego_curve_data(rego_dates: pd.DataFrame, rego_counts: pd.DataFrame):
    """_summary_

    Args:
        rego_dates (pd.DataFrame): Dataframe containing the registration dates data.
        rego_counts (pd.DataFrame): Dataframe containing the registration counts data.
    """
    pre_season_rego_curve = (
        rego_dates.groupby(["season", "days_before_first_game"])["id"]
        .count()
        .reset_index()
    )
    pre_season_rego_curve = pre_season_rego_curve.merge(
        rego_counts, on="season", how="inner"
    ).sort_values("days_before_first_game")
    pre_season_rego_curve.loc[:, "registrations_percent"] = (
        pre_season_rego_curve["id"] / pre_season_rego_curve["total_registrations"]
    )
    cummulative_percent = (
        pre_season_rego_curve.rename(
            columns={"registrations_percent": "cummlative_registrations_percent"}
        )
        .groupby("season")["cummlative_registrations_percent"]
        .cumsum()
    )
    return pre_season_rego_curve.merge(
        cummulative_percent, left_index=True, right_index=True
    )


def registration_count() -> pd.DataFrame:
    """Extact the registrations count before the start of the season.

    Retuns:
        pd.DataFrame: The results of the query.
    """
    return read_data(
        f"""
            with first_game_dates as (
                select
                    season,
                    date(min(start_ts)) as first_game_date
                from games
                group by
                    season
            ),

            registration_dates as (
                select
                    id,
                    season,
                    registered_date::date as registered_date
                from registrations
            ),

            days_before_first_game as (
                select
                    season,
                    first_game_date,
                    registered_date,
                    registered_date::date - first_game_date::date as days_before_first_game
                from registration_dates
                inner join first_game_dates
                using(season)
            ),

            registration_count as (
                select
                    season,
                    count(*) as total_registrations
                from days_before_first_game
                where
                    days_before_first_game <= 0
                group by
                    season
            )

            select *
            from registration_count
    """
    )


def registration_dates() -> pd.DataFrame:
    """Extact the registrations dates before the start of the season.

    Retuns:
        pd.DataFrame: The results of the query.
    """
    return read_data(
        f"""
            with first_game_dates as (
                select
                    season,
                    date(min(start_ts)) as first_game_date
                from games
                group by
                    season
            ),

            registration_dates as (
                select
                    id,
                    season,
                    team,
                    registered_date::date as registered_date
                from registrations
            ),

            days_before_first_game as (
                select
                    id,
                    season,
                    team,
                    first_game_date,
                    registered_date,
                    registered_date::date - first_game_date::date as days_before_first_game
                from registration_dates
                inner join first_game_dates
                using(season)
            )

            select *
            from days_before_first_game
            where days_before_first_game <= 0
    """
    )


def get_line_chart(
    data: pd.DataFrame,
    date_col: str,
    y_col: str,
    by_group: str,
    use_container_width: bool = True,
):
    hover = alt.selection_single(
        fields=[date_col],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data)
        .mark_line()
        .encode(
            x=date_col,
            y=y_col,
            color=alt.Color(by_group, scale={"range": ["#0d5903", "#1bcc04"]}),
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
