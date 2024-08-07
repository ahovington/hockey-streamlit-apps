import streamlit as st
import pandas as pd
import altair as alt

from config import config
from utils import auth_validation
from registration.models import registration_count, registration_dates


@auth_validation
def main() -> None:
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

    # registrations pre season curves
    pre_season_rego_curve_by_season = rego_curve_data(rego_dates, rego_counts)
    get_line_chart(
        pre_season_rego_curve_by_season,
        "days_before_first_game",
        "cummlative_registrations_percent",
        "season",
    )

    config.app.seasons.sort(reverse=True)
    season = st.selectbox(
        "Season", config.app.seasons, index=0, placeholder="Select season..."
    )
    pre_season_rego_curve_by_team = rego_curve_data(
        rego_dates[rego_dates["season"] == season], rego_counts, groupby_team=True
    )
    get_line_chart(
        pre_season_rego_curve_by_team,
        "days_before_first_game",
        "cummlative_registrations_percent",
        "team",
    )


def rego_curve_data(
    rego_dates: pd.DataFrame, rego_counts: pd.DataFrame, groupby_team: bool = False
):
    """_summary_

    Args:
        rego_dates (pd.DataFrame): Dataframe containing the registration dates data.
        rego_counts (pd.DataFrame): Dataframe containing the registration counts data.
    """
    by_group = ["season", "days_before_first_game"]
    if groupby_team:
        by_group += ["team"]
    pre_season_rego_curve = rego_dates.groupby(by_group)["id"].count().reset_index()
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
        .groupby("team" if groupby_team else "season")[
            "cummlative_registrations_percent"
        ]
        .cumsum()
    )
    return pre_season_rego_curve.merge(
        cummulative_percent, left_index=True, right_index=True
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
            color=alt.Color(by_group, scale={"range": ["#008000", "#2AAA8A"]}),
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
                alt.Tooltip(date_col, title="Days before the first game"),
                alt.Tooltip(y_col, title="Percent of players registered"),
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


main()
