from typing import Optional
import pandas as pd

from utils import read_data


def game_rounds() -> pd.DataFrame:
    df = read_data(
        """
        select
            distinct
            round,
            case
                when round = 'SF1' then '30'
                when round = 'PF1' then '40'
                when round = 'GF1' then '30'
                else round
            end as round_order
        from games
        """
    )
    df.loc[:, "round_order"] = df.loc[:, "round_order"].astype(float)
    df = df.sort_values("round_order")["round"]
    return df


def game_results_data(
    season: str, team: Optional[str] = None, game_round: Optional[str] = None
) -> pd.DataFrame:
    """Extact the outstanding club fees.

    Args:
        season (str): The hockey season, usually the calendar year.
        team (str, optional): The teams name.
        game_round (str, optional): The round of the season.

    Retuns:
        pd.DataFrame: The results of the query.
    """
    filters = ["where", f"g.season = '{ season }'"]
    if team:
        filters.append("and")
        filters.append(f"t.team || ' - ' || t.grade = '{ team }'")
    if game_round:
        filters.append("and")
        filters.append(f"g.round = '{ game_round }'")
    df = read_data(
        f"""
        select
            g.id,
            t.team,
            t.grade,
            t.team || ' - ' || t.grade as team_name,
            g.season,
            g.round,
            case
                when l.name = 'Newcastle International Hockey Centre'
                then 'NIHC'
                else l.name
            end as location_name,
            l.field,
            g.finals,
            case
                when g.opposition = '4thGreen' then 'West Green'
                when g.opposition = '4thRed' then 'West Red'
                else g.opposition 
            end as opposition,
            g.start_ts,
            g.goals_for,
            g.goals_against,
            case
                when g.goals_for > g.goals_against then 'win'
                when g.goals_for < g.goals_against then 'loss'
                when g.goals_for = g.goals_against then 'draw'
            end as result,
            g.goals_for > g.goals_against as win,
            g.goals_for < g.goals_against as loss,
            g.goals_for = g.goals_against as draw
        from games as g
        left join teams as t
        on g.team_id = t.id
        left join locations as l
        on g.location_id = l.id
        { " ".join(filters) }
        order by
            t.team_order,
            g.start_ts
        """
    )
    df.loc[:, "goals_for"] = (
        df.loc[:, "goals_for"].replace("", 0).astype(float).astype(int)
    )
    df.loc[:, "goals_against"] = (
        df.loc[:, "goals_against"].replace("", 0).astype(float).astype(int)
    )
    return df
