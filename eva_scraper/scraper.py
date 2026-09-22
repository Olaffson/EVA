from .client import EvaClient
from .db import upsert_game, upsert_game_player
from .queries import DASHBOARD_LAST_MATCHES_QUERY

GAME_TYPE = "BattleArena"


def scrape_last_matches(client: EvaClient, conn, *, user_id: int, season_id: int) -> int:
    data = client.graphql(
        "DashboardLastMatches",
        DASHBOARD_LAST_MATCHES_QUERY,
        {"userId": user_id, "seasonId": season_id},
    )
    games = data["listLastAfterhGameHistoriesByUserAndSeason"]

    for game in games:
        upsert_game(
            conn,
            game_id=game["id"],
            season_id=season_id,
            game_type=GAME_TYPE,
            created_at=game["createdAt"],
            mode_id=game["mode"]["id"],
            mode_identifier=game["mode"]["identifier"],
            map_id=game["map"]["id"],
            map_name=game["map"]["name"],
        )
        for player in game["players"]:
            upsert_game_player(
                conn,
                game_id=game["id"],
                user_id=player["userId"],
                is_mvp=player["isMvp"],
                outcome=player["data"]["outcome"],
                kills=player["data"]["kills"],
                deaths=player["data"]["deaths"],
                assists=player["data"]["assists"],
            )

    conn.commit()
    return len(games)
