import pandas as pd

from utils import read_data


def player_data(player_id: str, season: str) -> pd.DataFrame:
    """The data for the player

    Args:
        player_id str: The id of the player.
        season str: The hockey season.
    """
    df = read_data(
        f"""
       select
            p.id as player_id,
            p.full_name as player,
            g.id as game_id,
            t.team,
            r.grade as player_graded,
            t.grade,
            s.goal_keeper,
            s.played,
            g.season,
            g.round,
            case
                when l.name = 'Newcastle International Hockey Centre'
                then 'NIHC'
                else l.name
            end as location_name,
            g.finals,
            case
                when g.opposition = '4thGreen' then 'West Green'
                when g.opposition = '4thRed' then 'West Red'
                else g.opposition 
            end as opposition,
            g.start_ts,
            g.goals_for,
            g.goals_against,
            coalesce(re.goals, 0) as goals,
            coalesce(re.green_card, 0) as green_card,
            coalesce(re.yellow_card, 0) as yellow_card,
            coalesce(re.red_card, 0) as red_card,
            coalesce(re.green_card, 0) + coalesce(re.yellow_card, 0) + coalesce(re.red_card, 0) as cards
        from players as p
        inner join registrations as r
        on p.id = r.player_id
        inner join selections as s
        on p.id = s.player_id
        left join results as re
        on s.id = re.id
        inner join games as g
        on s.game_id = g.id and
            r.season = g.season
        inner join teams as t
        on g.team_id = t.id
         inner join locations as l
        on g.location_id = l.id
        where
            s.played = true and
            p.id = '{player_id}' and
            r.season = '{season}'
        """
    )
    df.loc[:, "goals_for"] = (
        df.loc[:, "goals_for"].replace("", 0).astype(float).astype(int)
    )
    df.loc[:, "goals_against"] = (
        df.loc[:, "goals_against"].replace("", 0).astype(float).astype(int)
    )
    return df


def player_names(season: str) -> pd.DataFrame:
    return read_data(
        f"""
        with _goals as (
            select
                s.player_id,
                sum(r.goals) as goals

            from games as g
            inner join selections as s
            on g.id = s.game_id
            inner join results as r
            on s.id = r.id
            where
                s.played = true and
                g.season = '{season}'
            group by
                s.player_id
        )

        select
            p.id,
            p.full_name as player
        from registrations as r
        inner join players as p
        on r.player_id = p.id
        left join _goals as g
        on p.id = g.player_id
        where r.season = '{season}'
        order by
            coalesce(g.goals, 0) desc
        """
    )
