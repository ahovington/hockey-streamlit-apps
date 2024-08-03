import pandas as pd

from utils import read_data


def player_data(player_name: str, season: str) -> pd.DataFrame:
    """The data for the player

    Args:
        player_name str: The name of the player.
        season str: The hockey season.
    """
    return read_data(
        f"""
            select
                p.id as player_id,
                p.full_name as player,
                g.season,
                r.grade as player_graded,
                t.grade as grade_played,
                s.goal_keeper,
                s.played,
                count(*) as games_played
            from players as p
            left join registrations as r
            on p.id = r.player_id
            left join selections as s
            on p.id = s.player_id
            left join games as g
            on s.game_id = g.id and
                r.season = g.season
            left join teams as t
            on g.team_id = t.id
            where
                s.played = true and
                p.full_name = '{ player_name }' and
                r.season = '{ season }' and
                g.season = '{ season }'
            group by
                p.id,
                p.full_name,
                g.season,
                r.grade,
                t.grade,
                s.goal_keeper,
                s.played
            order by
                p.id
    """
    )


def player_names() -> pd.DataFrame:
    return read_data("select full_name as player from players order by full_name")
