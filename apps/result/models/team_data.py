import pandas as pd

from utils import read_data


def team_results_data(season: str) -> pd.DataFrame:
    """Extact the outstanding club fees.

    Args:
        season (str): The hockey season, usually the calendar year.
        team (str, optional): The teams name.
        game_round (str, optional): The round of the season.

    Retuns:
        pd.DataFrame: The results of the query.
    """
    df = read_data(
        # TODO: filter out upcoming games
        f"""
        with game_data as (
            select
                g.id,
                t.team_order,
                t.team,
                t.grade,
                t.team || ' - ' || t.grade as team_name,
                g.season,
                g.goals_for,
                g.goals_against,
                g.goals_for > g.goals_against as win,
                g.goals_for < g.goals_against as loss,
                g.goals_for = g.goals_against as draw
            from games as g
            left join teams as t
            on g.team_id = t.id
            where g.season = '{ season }'
        )

        select
            team_order,
            team,
            grade,
            team_name,
            goals_for,
            goals_against,
            1 as games_played,
            win,
            loss,
            draw
        from game_data as gd
        """
    )
    df.loc[:, "goals_for"] = (
        df.loc[:, "goals_for"].replace("", 0).astype(float).astype(int)
    )
    df.loc[:, "goals_against"] = (
        df.loc[:, "goals_against"].replace("", 0).astype(float).astype(int)
    )
    df = (
        df.groupby(["team_order", "team", "grade", "team_name"])
        .agg(
            {
                "games_played": "sum",
                "goals_for": "sum",
                "goals_against": "sum",
                "win": "sum",
                "loss": "sum",
                "draw": "sum",
            }
        )
        .reset_index()
    )

    return df


def team_names(season: str) -> pd.DataFrame:
    return read_data(
        f"""
            select
                distinct
                team || ' - ' || grade as team_name,
                team_order
            from teams
            where
                season = '{season}'
            order by
                team_order
        """
    )
