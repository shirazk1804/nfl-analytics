import polars as pl

# ============================================================
# TEAM RANKINGS
# ============================================================

def get_team_rank(all_team_stats, team, stat, higher_is_better=True):
    sorted_teams = sorted(
        all_team_stats,
        key=lambda x: x[stat],
        reverse=higher_is_better
    )

    for rank, team_stats in enumerate(sorted_teams, start=1):
        if team_stats["team"] == team:
            return rank
        
    return None

# ============================================================
# DATA FILTERING
# ============================================================

# Filters the full NFL schedule to games involving one team
def get_team_games(games, team):
    team_games = games.filter(
        (games["home_team"] == team) | (games["away_team"] == team)
    )

    return team_games

# ============================================================
# RECORD CALCULATIONS
# ============================================================

# Calculates wins, losses, and ties for a team's set of games
def calculate_record(team_games, team):
    wins = 0
    losses = 0
    ties = 0

    for game in team_games.iter_rows(named=True):

        # Determine the team's score based on whether it was home or away
        if game["home_team"] == team:
            team_score = game["home_score"]
            opponent_score = game["away_score"]
        else:
            team_score = game["away_score"]
            opponent_score = game["home_score"]

        # Determine the result of the game
        if team_score > opponent_score:
            wins += 1
        elif team_score < opponent_score:
            losses += 1
        else:
            ties += 1

    return wins, losses, ties

# ============================================================
# TEAM STATISTICS
# ============================================================

# Calculates scoring, point differential, win percentage,
# and home/away records
def calculate_team_stats(regular_season_games, team, wins, ties):
    points_scored = 0
    points_allowed = 0

    home_wins = 0
    home_losses = 0
    home_ties = 0

    away_wins = 0
    away_losses = 0
    away_ties = 0

    for game in regular_season_games.iter_rows(named=True):

        if game["home_team"] == team:
            team_score = game["home_score"]
            opponent_score = game["away_score"]

            if team_score > opponent_score:
                home_wins += 1
            elif team_score < opponent_score:
                home_losses += 1
            else:
                home_ties += 1

        else:
            team_score = game["away_score"]
            opponent_score = game["home_score"]

            if team_score > opponent_score:
                away_wins += 1
            elif team_score < opponent_score:
                away_losses += 1
            else:
                away_ties += 1

        points_scored += team_score
        points_allowed += opponent_score

    games_played = len(regular_season_games)

    point_differential = points_scored - points_allowed
    points_per_game = points_scored / games_played
    points_allowed_per_game = points_allowed / games_played

    # NFL ties count for half a win when calculating win percentage
    win_percentage = ((wins + (ties * 0.5)) / games_played) * 100

    return {
        "points_scored": points_scored,
        "points_allowed": points_allowed,
        "point_differential": point_differential,
        "points_per_game": points_per_game,
        "points_allowed_per_game": points_allowed_per_game,
        "win_percentage": win_percentage,
        "home_wins": home_wins,
        "home_losses": home_losses,
        "home_ties": home_ties,
        "away_wins": away_wins,
        "away_losses": away_losses,
        "away_ties": away_ties
    }

# ============================================================
# OFFENSIVE STATISTICS
# ============================================================

# Calculates regular-season passing, rushing, and total offense
def calculate_offensive_stats(pbp, team, games_played):

    # Keep only regular-season offensive plays for the selected team
    team_pbp = pbp.filter(
        (pbp["posteam"] == team) &
        (pbp["season_type"] == "REG")
    )

    successful_plays = team_pbp.filter(
        (
        (pl.col("pass_attempt") == 1) &
        (pl.col("rush_attempt") == 1)
        ) &
        pl.col("success").is_not_null()
    )

    if len(successful_plays) > 0:
        offensive_success_rate = (
            successful_plays["success"].mean()
        )
    else:
        offensive_success_rate = 0
    

    epa_plays = team_pbp.filter(
        (
            (pl.col("pass_attempt") == 1) |
            (pl.col("rush_attempt") == 1) 
        ) &
        pl.col("epa").is_not_null()
    )

    if len(epa_plays) > 0:
        offensive_epa_per_play = epa_plays["epa"].mean()
    else:
        offensive_epa_per_play = 0

    # Offensive Yards
    passing_yards = team_pbp["passing_yards"].sum()
    rushing_yards = team_pbp["rushing_yards"].sum()

    # Touchdowns
    passing_touchdowns = team_pbp["pass_touchdown"].sum()
    rushing_touchdowns = team_pbp["rush_touchdown"].sum()
    total_touchdowns = passing_touchdowns + rushing_touchdowns

    # Turnovers
    interceptions = team_pbp["interception"].sum()
    fumbles_lost = team_pbp["fumble_lost"].sum()
    total_turnovers = interceptions + fumbles_lost

    total_yards = passing_yards + rushing_yards

    passing_yards_per_game = passing_yards / games_played
    rushing_yards_per_game = rushing_yards / games_played
    total_yards_per_game = total_yards / games_played

    # Efficiency Stats
    pass_attempts = team_pbp["pass_attempt"].sum()
    rush_attempts = team_pbp["rush_attempt"].sum()

    total_plays = pass_attempts + rush_attempts

    yards_per_play = total_yards / total_plays
    passing_yards_per_attempt = passing_yards / pass_attempts
    rushing_yards_per_attempt = rushing_yards / rush_attempts

    return {
        "passing_yards": passing_yards,
        "rushing_yards": rushing_yards,
        "total_yards": total_yards,
        "passing_yards_per_game": passing_yards_per_game,
        "rushing_yards_per_game": rushing_yards_per_game,
        "total_yards_per_game": total_yards_per_game,
        "passing_touchdowns": passing_touchdowns,
        "rushing_touchdowns": rushing_touchdowns,
        "total_touchdowns": total_touchdowns,
        "interceptions": interceptions,
        "fumbles_lost": fumbles_lost,
        "total_turnovers": total_turnovers,
        "pass_attempts": pass_attempts,
        "rush_attempts": rush_attempts,
        "total_plays": total_plays,
        "yards_per_play": yards_per_play,
        "passing_yards_per_attempt": passing_yards_per_attempt,
        "rushing_yards_per_attempt": rushing_yards_per_attempt,
        "offensive_epa_per_play": offensive_epa_per_play,
        "offensive_success_rate": offensive_success_rate
    }

# Single Player Passing Statistics
def calculate_passing_stats(pbp, team):
    team_pbp = pbp.filter(
        (pbp["posteam"] == team) &
        (pbp["season_type"] == "REG") &
        (pbp["pass_attempt"] == 1)
    )

    passing_stats = {}

    for play in team_pbp.iter_rows(named=True):
        passer = play["passer_player_name"]

        # Skips plays that do not have a passer
        if passer is None:
            continue

        # Create a new entry when we see a new passer for the first time
        if passer not in passing_stats:
            passing_stats[passer] = {
                "attempts": 0,
                "completions": 0,
                "yards": 0,
                "touchdowns": 0,
                "interceptions": 0
            }
        
        passing_stats[passer]["attempts"] += 1

        if play["complete_pass"] == 1:
            passing_stats[passer]["completions"] += 1
        
        if play["passing_yards"] is not None:
            passing_stats[passer]["yards"] += play["passing_yards"]
        
        if play["pass_touchdown"] == 1:
            passing_stats[passer]["touchdowns"] += 1
        
        if play["interception"] == 1:
            passing_stats[passer]["interceptions"] += 1
        
    return passing_stats

# Calculates Single Player Rushing Stats
def calculate_rushing_stats(pbp, team):
    team_pbp = pbp.filter(
        (pbp["posteam"] == team) &
        (pbp["season_type"] == "REG") & 
        (pbp["rush_attempt"] == 1)
    )

    rushing_stats = {}

    for play in team_pbp.iter_rows(named=True):
        rusher = play["rusher_player_name"]

        # Skips plays that do not have a rush attempt
        if rusher is None:
            continue

        # Creates a new entry for a new rusher
        if rusher not in rushing_stats:
            rushing_stats[rusher] = {
                "attempts": 0,
                "yards": 0,
                "touchdowns": 0
            }
        
        rushing_stats[rusher]["attempts"] += 1

        if play["rushing_yards"] is not None:
            rushing_stats[rusher]["yards"] += play["rushing_yards"]

        if play["rush_touchdown"] == 1:
            rushing_stats[rusher]["touchdowns"] += 1
        
    return rushing_stats

# Calculates Single Player Receiving Stats
def calculate_receiving_stats(pbp, team):
    team_pbp = pbp.filter(
        (pbp["posteam"] == team) &
        (pbp["season_type"] == "REG") &
        (pbp["pass_attempt"] == 1)
    )

    receiving_stats = {}

    for play in team_pbp.iter_rows(named=True):
        receiver = play["receiver_player_name"]

        # Skips plays without a receiver
        if receiver is None:
            continue

        # Creates new entry for each new receiver
        if receiver not in receiving_stats:
            receiving_stats[receiver] = {
                "targets": 0,
                "receptions": 0,
                "yards": 0,
                "touchdowns": 0
            }
        
        receiving_stats[receiver]["targets"] += 1

        if play["complete_pass"] == 1:
            receiving_stats[receiver]["receptions"] += 1
        
        if play["receiving_yards"] is not None:
            receiving_stats[receiver]["yards"] += play["receiving_yards"]
        
        if play["pass_touchdown"] == 1:
            receiving_stats[receiver]["touchdowns"] += 1
    
    return receiving_stats

# ============================================================
# DEFENSIVE STATISTICS
# ============================================================

def calculate_defensive_stats(pbp, team, games_played):
    team_defense = pbp.filter(
        (pbp["defteam"] == team) &
        (pbp["season_type"] == "REG")
    )

    defensive_success_plays = team_defense.filter(
        (
        (pl.col("pass_attempt") == 1) | 
        (pl.col("rush_attempt") == 1)
        ) &
        pl.col("success").is_not_null()
    )

    if len(defensive_success_plays) > 0:
        defensive_success_rate = (
            1 - defensive_success_plays["success"].mean()
        )
    else:
        defensive_success_rate = 0

    epa_plays_allowed = team_defense.filter(
        (
            (pl.col("pass_attempt") == 1) |
            (pl.col("rush_attempt") == 1)
        ) &
        pl.col("epa").is_not_null()
    )

    if len(epa_plays_allowed) > 0:
        defensive_epa_per_play = -epa_plays_allowed["epa"].mean()
    else:
        defensive_epa_per_play = 0

    # Yards Allowed
    passing_yards_allowed = team_defense["passing_yards"].sum()
    rushing_yards_allowed = team_defense["rushing_yards"].sum()
    total_yards_allowed = passing_yards_allowed + rushing_yards_allowed

    # Yards Allowed Per Game
    passing_yards_allowed_per_game = passing_yards_allowed / games_played
    rushing_yards_allowed_per_game = rushing_yards_allowed / games_played

    # Defensive Plays
    pass_attempts_faced = team_defense["pass_attempt"].sum()
    rush_attempts_faced = team_defense["rush_attempt"].sum()
    total_plays_faced = pass_attempts_faced + rush_attempts_faced

    # Big Defensive Plays
    sacks = team_defense["sack"].sum()
    interceptions = team_defense["interception"].sum()
    fumbles_recovered = team_defense["fumble_lost"].sum()

    takeaways = interceptions + fumbles_recovered

    # Per Game Stats
    yards_allowed_per_game = total_yards_allowed / games_played

    # Efficiency
    yards_allowed_per_play = total_yards_allowed / total_plays_faced

    return {
        "passing_yards_allowed": passing_yards_allowed,
        "rushing_yards_allowed": rushing_yards_allowed,
        "total_yards_allowed": total_yards_allowed,
        "yards_allowed_per_game": yards_allowed_per_game,
        "passing_yards_allowed_per_game": passing_yards_allowed_per_game,
        "rushing_yards_allowed_per_game": rushing_yards_allowed_per_game,
        "yards_allowed_per_play": yards_allowed_per_play,
        "sacks": sacks,
        "interceptions": interceptions,
        "fumbles_recovered": fumbles_recovered,
        "takeaways": takeaways,
        "defensive_epa_per_play": defensive_epa_per_play,
        "defensive_success_rate": defensive_success_rate
    }

# ============================================================
# SPECIAL TEAMS STATISTICS
# ============================================================

def calculate_special_teams_stats(pbp, team):

    special_teams_plays = pbp.filter(
        (pl.col("season_type") == "REG") &
        (pl.col("special_teams_play") == 1) &
        pl.col("epa").is_not_null() &
        (
            (pl.col("posteam") == team) |
            (pl.col("defteam") == team)
        )
    )

    if len(special_teams_plays) == 0:
        return {
            "special_teams_epa_per_play": 0
        }
    
    team_epa = special_teams_plays.select(
        pl.when(
            pl.col("posteam") == team
        )
        .then(pl.col("epa"))
        .otherwise(-pl.col("epa"))
        .mean()
        .alias("special_teams_epa_per_play")
    ).item()

    return {
        "special_teams_epa_per_play": team_epa
    }

# ============================================================
# NFL TEAM RANKINGS
# ============================================================

def calculate_team_rankings(games, pbp):
    regular_games = games.filter(
        games["game_type"] == "REG"
    )

    teams = sorted(
        set(regular_games["home_team"].to_list()) |
        set(regular_games["away_team"].to_list())
    )

    all_team_stats = []

    for current_team in teams:
        current_team_games = get_team_games(
            regular_games,
            current_team
        )

        wins, losses, ties = calculate_record(
            current_team_games,
            current_team
        )

        games_played = len(current_team_games)

        team_stats = calculate_team_stats(
            current_team_games,
            current_team,
            wins,
            ties
        )

        offensive_stats = calculate_offensive_stats(
            pbp,
            current_team,
            games_played
        )

        defensive_stats = calculate_defensive_stats(
            pbp,
            current_team,
            games_played
        )

        special_teams_stats = calculate_special_teams_stats(
            pbp,
            current_team
        )

        turnover_differential = (
            defensive_stats["takeaways"] -
            offensive_stats["total_turnovers"]
        )

        all_team_stats.append({
            "team": current_team,

            "games_played": games_played,

            "points_per_game":
                team_stats["points_per_game"],

            "points_allowed_per_game":
                team_stats["points_allowed_per_game"],
            
            "win_percentage":
                team_stats["win_percentage"],
            
            "total_yards_per_game":
                offensive_stats["total_yards_per_game"],
            
            "passing_yards_per_game":
                offensive_stats["passing_yards_per_game"],

            "rushing_yards_per_game":
                offensive_stats["rushing_yards_per_game"],
            
            "yards_per_play":
                offensive_stats["yards_per_play"],
            
            "passing_yards_per_attempt":
                offensive_stats["passing_yards_per_attempt"],
            
            "rushing_yards_per_attempt":
                offensive_stats["rushing_yards_per_attempt"],
            
            "offensive_epa_per_play":
                offensive_stats["offensive_epa_per_play"],
            
            "yards_allowed_per_game":
                defensive_stats["yards_allowed_per_game"],
            
            "yards_allowed_per_play":
                defensive_stats["yards_allowed_per_play"],
            
            "passing_yards_allowed_per_game":
                defensive_stats["passing_yards_allowed"]
                / games_played,
            
            "rushing_yards_allowed_per_game":
                defensive_stats["rushing_yards_allowed"]
                / games_played,
            
            "defensive_epa_per_play":
                defensive_stats["defensive_epa_per_play"],
            
            "special_teams_epa_per_play":
                special_teams_stats["special_teams_epa_per_play"],
            
            "offensive_success_rate":
                offensive_stats["offensive_success_rate"],

            "defensive_success_rate":
                defensive_stats["defensive_success_rate"],
            
            "turnover_differential":
                turnover_differential

        })
    
    return all_team_stats

# ============================================================
# RECENT TEAM FORM
# ============================================================

def calculate_recent_form(games, team, num_games = 3):

    team_games = get_team_games(
        games,
        team
    ).sort("week")

    # Keep only recent games
    recent_games = team_games.tail(num_games)

    games_played = len(recent_games)

    if games_played == 0:
        return {
            "points_per_games": 0,
            "points_allowed_per_game": 0,
            "win_percentage": 0
        }
    
    points_scored = 0
    points_allowed = 0
    wins = 0
    ties = 0

    for game in recent_games.iter_rows(named=True):

        if game["home_team"] == team:
            team_score = game["home_score"]
            opponent_score = game["away_score"]
        else:
            team_score = game["away_score"]
            opponent_score = game["home_score"]
    
    points_scored += team_score
    points_allowed += opponent_score

    if team_score > opponent_score:
        wins += 1
    elif team_score == opponent_score:
        ties += 1
    
    points_per_game = (
        points_scored / games_played
    )

    points_allowed_per_game = (
        points_allowed / games_played
    )

    win_percentage = (
        (wins + (ties * 0.5)) /
        games_played
    ) * 100

    return {
        "points_per_game": points_per_game,
        "points_allowed_per_game": points_allowed_per_game,
        "win_percentage": win_percentage
    }

# ============================================================
# ELO RATINGS
# ============================================================

def calculate_elo_ratings(
    games,
    base_rating=1500,
    k_factor=20,
    initial_ratings=None
):

    teams = (
        set(games["home_team"].to_list()) |
        set(games["away_team"].to_list())
    )

    if initial_ratings is None:
        ratings = {}
    else:
        ratings = {
            team: float(rating)
            for team, rating in initial_ratings.items()
        }

    # Any team without an existing rating starts at 1500
    for team in teams:
        ratings.setdefault(
            team,
            float(base_rating)
        )

    games = games.sort("week")

    for game in games.iter_rows(named=True):

        home_team = game["home_team"]
        away_team = game["away_team"]

        home_score = game["home_score"]
        away_score = game["away_score"]

        if home_score is None or away_score is None:
            continue

        home_elo = ratings[home_team]
        away_elo = ratings[away_team]

        expected_home = (
            1 /
            (
                1 +
                10 ** (
                    (away_elo - home_elo) / 400
                )
            )
        )

        if home_score > away_score:
            actual_home = 1
        elif home_score < away_score:
            actual_home = 0
        else:
            actual_home = 0.5

        rating_change = (
            k_factor *
            (actual_home - expected_home)
        )

        ratings[home_team] += rating_change
        ratings[away_team] -= rating_change

    return ratings

# ============================================================
# REST AND BYE WEEK FEATURES
# ============================================================

from datetime import date, datetime

def convert_to_date(value):

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    return date.fromisoformat(
        str(value)[:10]
    )

def calculate_rest_features(
        previous_games,
        team,
        current_game_date,
        current_week
):
    team_games = get_team_games(
        previous_games,
        team
    ).sort("gameday")

    # Fallback if the team has no previous games
    if len(team_games) == 0:
        return {
            "days_rest": 7,
            "after_bye": 0
        }

    last_game = team_games.tail(1).row(
        0,
        named=True
    )

    last_game_date = convert_to_date(
        last_game["gameday"]
    )

    current_game_date = convert_to_date(
        current_game_date
    )

    days_rest = (
        current_game_date - last_game_date
    ).days

    week_gap = (
        current_week - last_game["week"]
    )

    if week_gap > 1:
        after_bye = 1
    else:
        after_bye = 0

    return {
        "days_rest": days_rest,
        "after_bye": after_bye
    }

# ============================================================
# QB STATISTICS
# ============================================================

def calculate_qb_features(pbp, team):

    passing_plays = pbp.filter(
        (pl.col("posteam") == team) &
        (pl.col("season_type") == "REG") &
        (pl.col("pass_attempt") == 1) &
        pl.col("passer_player_name").is_not_null()
    )

    if len(passing_plays) == 0:
        return {
            "qb_epa_per_play": 0,
            "qb_yards_per_attempt": 0,
            "qb_td_rate": 0,
            "qb_interception_rate": 0
        }

    recent_weeks = (
        passing_plays["week"]
        .unique()
        .sort(descending=True)
        .head(2)
    )

    recent_passing_plays = passing_plays.filter(
        pl.col("week").is_in(recent_weeks)
    )

    passer_attempts = {}

    for play in recent_passing_plays.iter_rows(named=True):

        passer = play["passer_player_name"]

        if passer not in passer_attempts:
            passer_attempts[passer] = 0

        passer_attempts[passer] += 1

    primary_qb = max(
        passer_attempts,
        key=passer_attempts.get
    )

    qb_plays = passing_plays.filter(
        pl.col("passer_player_name") == primary_qb
    )

    attempts = len(qb_plays)

    passing_yards = qb_plays[
        "passing_yards"
    ].sum()

    touchdowns = qb_plays[
        "pass_touchdown"
    ].sum()

    interceptions = qb_plays[
        "interception"
    ].sum()

    qb_epa_per_play = qb_plays[
        "epa"
    ].mean()

    qb_yards_per_attempt = (
        passing_yards / attempts
    )

    qb_td_rate = (
        touchdowns / attempts
    )

    qb_interception_rate = (
        interceptions / attempts
    )

    return {
        "qb_epa_per_play": qb_epa_per_play,
        "qb_yards_per_attempt": qb_yards_per_attempt,
        "qb_td_rate": qb_td_rate,
        "qb_interception_rate": qb_interception_rate
    }