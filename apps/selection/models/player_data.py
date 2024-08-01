import pandas as pd

from utils import read_data


def player_data(season: str, team_round: str, team: str) -> pd.DataFrame:
    """Extact the player data for the team and round.

    Args:
        season (str): The hockey season, usually the calendar year.
        team_round (str): The teams round of the season.
        team (str): The team results are being updated for.

    Retuns:
        pd.DataFrame: The results of the query.
    """
    df = read_data(
        f"""
        with _games as (
            select
                g.id as game_id,
                t.id as team_id,
                t.team_order,
                t.team || ' - ' || t.grade as team_name,
                g.round,
                g.opposition,
                g.start_ts
            from games as g
            inner join teams as t
            on g.team_id = t.id
            where
                g.season = '{ season }'
                and g.round = '{ team_round }'
                and t.team || ' - ' || t.grade = '{ team }'
        ),

        _selections as (
            select
                s.id as selection_id,
                s.player_id,
                s.game_id,
                g.team_id,
                s.goal_keeper,
                s.selected,
                s.played
            from selections as s
            inner join _games as g
            on s.game_id = g.game_id
        ),

        _registered_players as (
            select
                g.game_id,
                p.id as player_id,
                p.full_name as players_name,
                r.grade as players_grade,
                g.team_order,
                g.team_name,
                g.round,
                g.opposition,
                g.start_ts
            from players as p
            inner join registrations as r
            on p.id = r.player_id
            cross join _games as g
            where
                r.season = '{ season }'
        ),

        _played_games as (
            select
                coalesce(s.selection_id, g.game_id || g.player_id) as selection_id,
                g.game_id,
                g.player_id,
                case
                    when r.id is null then true
                    else false
                end as create_results,
                case
                    when s.selection_id is null then true
                    else false
                end as create_selections,
                g.opposition,
                g.players_name,
                g.players_grade,
                coalesce(s.selected, False) as selected,
                coalesce(s.goal_keeper, False) as goal_keeper,
                coalesce(s.played, False) as played,
                coalesce(r.goals, 0) as goals,
                coalesce(r.green_card, 0)  as green_card,
                coalesce(r.yellow_card, 0)  as yellow_card,
                coalesce(r.red_card, 0)  as red_card
            from _registered_players as g
            left join _selections as s
            on
                s.game_id = g.game_id
                and s.player_id = g.player_id
            left join results as r
            on s.selection_id = r.id
        )

        select *
        from _played_games
        order by
            selected desc,
            goal_keeper desc,
            players_grade desc
        """
    )
    return df.astype(
        {
            "selected": bool,
            "goal_keeper": bool,
            "played": bool,
            "goals": int,
            "green_card": int,
            "yellow_card": int,
            "red_card": int,
        }
    )
