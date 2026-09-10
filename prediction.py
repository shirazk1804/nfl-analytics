# ============================================================
# MATCHUP PREDICTION
# ============================================================

def calculate_matchup_prediction(
    all_team_stats,
    team1,
    team2,
    home_team=None
):
    team1_stats = next(
        stats for stats in all_team_stats
        if stats["team"] == team1
    )

    team2_stats = next(
        stats for stats in all_team_stats
        if stats["team"] == team2
    )

    # --------------------------------------------------------
    # BASE SCORE PROJECTION
    # --------------------------------------------------------

    team1_projected_points = (
        team1_stats["points_per_game"] +
        team2_stats["points_allowed_per_game"]
    ) / 2

    team2_projected_points = (
        team2_stats["points_per_game"] +
        team1_stats["points_allowed_per_game"]
    ) / 2

    # --------------------------------------------------------
    # YARDAGE MATCHUP
    # --------------------------------------------------------

    team1_yard_advantage = (
        team1_stats["total_yards_per_game"] -
        team2_stats["yards_allowed_per_game"]
    )

    team2_yard_advantage = (
        team2_stats["total_yards_per_game"] -
        team1_stats["yards_allowed_per_game"]
    )

    # Every 25 yards of advantage adjusts the projection by 1 point
    team1_projected_points += team1_yard_advantage / 25
    team2_projected_points += team2_yard_advantage / 25

    # --------------------------------------------------------
    # TURNOVERS
    # --------------------------------------------------------

    team1_turnovers_per_game = (
        team1_stats["turnover_differential"] /
        team1_stats["games_played"]
    )

    team2_turnovers_per_game = (
        team2_stats["turnover_differential"] /
        team2_stats["games_played"]
    )

    turnover_advantage = (
        team1_turnovers_per_game -
        team2_turnovers_per_game
    )

    # Turnover advantage adjusts the score
    team1_projected_points += turnover_advantage
    team2_projected_points -= turnover_advantage

    # --------------------------------------------------------
    # HOME FIELD ADVANTAGE
    # --------------------------------------------------------

    if home_team == team1:
        team1_projected_points += 1.5

    elif home_team == team2:
        team2_projected_points += 1.5

    return {
        "team1_projected_points": team1_projected_points,
        "team2_projected_points": team2_projected_points
    }
