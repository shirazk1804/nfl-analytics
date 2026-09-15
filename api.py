from ml import (
    LOGISTIC_FEATURE_COLUMNS,
    build_matchup_features,
    build_prior_season_matchup_features
)

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from datetime import datetime
from zoneinfo import ZoneInfo

from model_io import load_model

import nflreadpy as nfl
import polars as pl

from stats import calculate_team_rankings


# ============================================================
# LOAD MACHINE LEARNING MODEL
# ============================================================

model = load_model(
    "logistic_model.joblib"
)


# ============================================================
# NFL DATA CACHE
# ============================================================

schedule_cache = {}
pbp_cache = {}


def get_schedule(season):

    if season not in schedule_cache:

        print(
            f"\nLoading {season} schedule..."
        )

        schedule_cache[season] = (
            nfl.load_schedules(season)
        )

    return schedule_cache[season]


def get_pbp(season):

    if season not in pbp_cache:

        print(
            f"\nLoading {season} play-by-play..."
        )

        pbp_cache[season] = (
            nfl.load_pbp(season)
        )

    return pbp_cache[season]


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="NFL Analytics API",
    description="NFL game analytics and machine learning predictions",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://nfl-analytics-zeta.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class PredictionRequest(BaseModel):

    season: int = 2025
    week: int
    home_team: str
    away_team: str


# ============================================================
# API ROUTES
# ============================================================

@app.get("/")
def home():

    return {
        "message": "NFL Analytics API is running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "model_loaded": True,
        "model_type": type(model).__name__
    }


# ============================================================
# WEEKLY SCHEDULE
# ============================================================

@app.get("/games/{season}/{week}")
def get_week_games(
    season: int,
    week: int
):

    games = get_schedule(
        season
    )

    week_games = games.filter(
        (pl.col("game_type") == "REG") &
        (pl.col("week") == week)
    )

    if len(week_games) == 0:

        raise HTTPException(
            status_code=404,
            detail=(
                f"No games found for "
                f"Week {week} of {season}."
            )
        )

    matchups = []

    for game in week_games.iter_rows(
        named=True
    ):

        away_score = game["away_score"]
        home_score = game["home_score"]

        completed = (
            away_score is not None and
            home_score is not None
        )

        matchups.append({
            "away_team":
                game["away_team"],

            "home_team":
                game["home_team"],

            "gameday":
                str(game["gameday"]),

            "away_score":
                away_score,

            "home_score":
                home_score,

            "completed":
                completed
        })

    return {
        "season": season,
        "week": week,
        "games": matchups
    }

# ============================================================
# MATCHUP TEAM STATS
# ============================================================

@app.get(
    "/matchup-stats/{season}/{week}/{away_team}/{home_team}"
)
def get_matchup_stats(
    season: int,
    week: int,
    away_team: str,
    home_team: str
):

    away_team = away_team.upper()
    home_team = home_team.upper()

    games = get_schedule(
        season
    )

    regular_games = games.filter(
        pl.col("game_type") == "REG"
    )

    # ------------------------------------------------------------
    # WEEK 1 USES PRIOR-SEASON STATS
    # ------------------------------------------------------------

    if week == 1:

        stats_season = season - 1

        stats_games = get_schedule(
            stats_season
        ).filter(
            pl.col("game_type") == "REG"
        )

        stats_pbp = get_pbp(
            stats_season
        ).filter(
            pl.col("season_type") == "REG"
        )

        through_week = 18

    else:

        stats_season = season

        stats_games = regular_games.filter(
            (pl.col("week") < week) &
            pl.col("home_score").is_not_null() &
            pl.col("away_score").is_not_null()
        )

        stats_pbp = get_pbp(
            season
        ).filter(
            (pl.col("season_type") == "REG") &
            (pl.col("week") < week)
        )

        through_week = week - 1

    # ------------------------------------------------------------
    # CALCULATE TEAM STATS
    # ------------------------------------------------------------

    all_team_stats = calculate_team_rankings(
        stats_games,
        stats_pbp
    )

    away_stats = next(
        (
            team
            for team in all_team_stats
            if team["team"] == away_team
        ),
        None
    )

    home_stats = next(
        (
            team
            for team in all_team_stats
            if team["team"] == home_team
        ),
        None
    )

    if away_stats is None or home_stats is None:

        raise HTTPException(
            status_code=404,
            detail="Team statistics are not available."
        )

    # ------------------------------------------------------------
    # CALCULATE RECORDS
    # ------------------------------------------------------------

    def get_record(team):

        team_games = stats_games.filter(
            (pl.col("home_team") == team) |
            (pl.col("away_team") == team)
        )

        wins = 0
        losses = 0
        ties = 0

        for game in team_games.iter_rows(
            named=True
        ):

            if game["home_team"] == team:

                team_score = game["home_score"]
                opponent_score = game["away_score"]

            else:

                team_score = game["away_score"]
                opponent_score = game["home_score"]

            if team_score > opponent_score:
                wins += 1

            elif team_score < opponent_score:
                losses += 1

            else:
                ties += 1

        return f"{wins}-{losses}-{ties}"

    # ------------------------------------------------------------
    # RESPONSE
    # ------------------------------------------------------------

    return {

        "stats_season":
            stats_season,

        "through_week":
            through_week,

        "away": {

            "team":
                away_team,

            "record":
                get_record(away_team),

            "points_per_game":
                round(
                    away_stats["points_per_game"],
                    1
                ),

            "points_allowed_per_game":
                round(
                    away_stats["points_allowed_per_game"],
                    1
                ),

            "yards_per_game":
                round(
                    away_stats["total_yards_per_game"],
                    1
                ),

            "yards_allowed_per_game":
                round(
                    away_stats["yards_allowed_per_game"],
                    1
                ),

            "epa_per_play":
                round(
                    away_stats["offensive_epa_per_play"],
                    3
                ),

            "epa_allowed_per_play":
                round(
                    away_stats["defensive_epa_per_play"],
                    3
                )
        },

        "home": {

            "team":
                home_team,

            "record":
                get_record(home_team),

            "points_per_game":
                round(
                    home_stats["points_per_game"],
                    1
                ),

            "points_allowed_per_game":
                round(
                    home_stats["points_allowed_per_game"],
                    1
                ),

            "yards_per_game":
                round(
                    home_stats["total_yards_per_game"],
                    1
                ),

            "yards_allowed_per_game":
                round(
                    home_stats["yards_allowed_per_game"],
                    1
                ),

            "epa_per_play":
                round(
                    home_stats["offensive_epa_per_play"],
                    3
                ),

            "epa_allowed_per_play":
                round(
                    home_stats["defensive_epa_per_play"],
                    3
                )
        }
    }

# ============================================================
# CURRENT NFL WEEK
# ============================================================

@app.get("/current-week/{season}")
def get_current_week(
    season: int
):

    games = get_schedule(
        season
    )

    regular_games = games.filter(
        pl.col("game_type") == "REG"
    )

    today = datetime.now(
        ZoneInfo("America/New_York")
    ).date()

    upcoming_weeks = []

    for game in regular_games.iter_rows(
        named=True
    ):

        game_date = game["gameday"]

        if isinstance(game_date, str):

            game_date = datetime.strptime(
                game_date,
                "%Y-%m-%d"
            ).date()

        elif isinstance(game_date, datetime):

            game_date = game_date.date()

        if game_date >= today:

            upcoming_weeks.append(
                game["week"]
            )

    if not upcoming_weeks:

        current_week = 18

    else:

        current_week = min(
            upcoming_weeks
        )

    return {
        "season": season,
        "week": current_week
    }

# ============================================================
# GAME PREDICTION
# ============================================================

@app.post("/predict")
def predict_game(
    request: PredictionRequest
):

    home_team = request.home_team.upper()
    away_team = request.away_team.upper()

    # ------------------------------------------------------------
    # LOAD CURRENT-SEASON SCHEDULE
    # ------------------------------------------------------------

    games = get_schedule(
        request.season
    )

    regular_games = games.filter(
        pl.col("game_type") == "REG"
    )

    # ------------------------------------------------------------
    # FIND SCHEDULED GAME
    # ------------------------------------------------------------

    scheduled_game = regular_games.filter(
        (pl.col("week") == request.week) &
        (pl.col("home_team") == home_team) &
        (pl.col("away_team") == away_team)
    )

    if len(scheduled_game) == 0:

        raise HTTPException(
            status_code=404,
            detail=(
                f"{away_team} @ {home_team} "
                f"was not found in Week "
                f"{request.week} of "
                f"{request.season}."
            )
        )

    game = scheduled_game.row(
        0,
        named=True
    )

    current_game_date = game["gameday"]

    # ------------------------------------------------------------
    # LOAD PRIOR-SEASON DATA
    # ------------------------------------------------------------

    prior_season = request.season - 1

    prior_games = get_schedule(
        prior_season
    )

    prior_pbp = get_pbp(
        prior_season
    )

    # ------------------------------------------------------------
    # BUILD PRIOR-SEASON FEATURES
    # ------------------------------------------------------------

    try:

        prior_features = (
            build_prior_season_matchup_features(
                games=prior_games,
                pbp=prior_pbp,
                season=prior_season,
                home_team=home_team,
                away_team=away_team
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    prior_feature_row = pl.DataFrame(
        [prior_features]
    )

    prior_model_input = (
        prior_feature_row
        .select(
            LOGISTIC_FEATURE_COLUMNS
        )
        .to_numpy()
    )

    prior_home_probability = (
        model.predict_proba(
            prior_model_input
        )[0][1]
    )

    # ------------------------------------------------------------
    # WEEK 1 ALWAYS USES PRIOR-SEASON DATA
    # ------------------------------------------------------------

    if request.week == 1:

        home_probability = (
            prior_home_probability
        )

        data_source = (
            f"{prior_season} season priors"
        )

    else:

        # --------------------------------------------------------
        # TRY TO LOAD CURRENT-SEASON PLAY-BY-PLAY
        # --------------------------------------------------------

        try:

            pbp = get_pbp(
                request.season
            )

        except ValueError:

            pbp = None

        # --------------------------------------------------------
        # FIND COMPLETED GAMES BEFORE SELECTED WEEK
        # --------------------------------------------------------

        completed_games = regular_games.filter(
            (pl.col("week") < request.week) &
            pl.col("home_score").is_not_null() &
            pl.col("away_score").is_not_null()
        )

        home_games_played = completed_games.filter(
            (pl.col("home_team") == home_team) |
            (pl.col("away_team") == home_team)
        ).height

        away_games_played = completed_games.filter(
            (pl.col("home_team") == away_team) |
            (pl.col("away_team") == away_team)
        ).height

        minimum_games_played = min(
            home_games_played,
            away_games_played
        )

        # --------------------------------------------------------
        # IF CURRENT DATA IS NOT READY, USE PRIOR SEASON
        # --------------------------------------------------------

        if (
            pbp is None or
            minimum_games_played == 0
        ):

            home_probability = (
                prior_home_probability
            )

            data_source = (
                f"{prior_season} season priors"
            )

        else:

            # ----------------------------------------------------
            # BUILD CURRENT-SEASON FEATURES
            # ----------------------------------------------------

            try:

                current_features = build_matchup_features(
                    games=games,
                    pbp=pbp,
                    season=request.season,
                    week=request.week,
                    home_team=home_team,
                    away_team=away_team,
                    current_game_date=current_game_date
                )

            except ValueError as error:

                raise HTTPException(
                    status_code=400,
                    detail=str(error)
                )

            current_feature_row = pl.DataFrame(
                [current_features]
            )

            current_model_input = (
                current_feature_row
                .select(
                    LOGISTIC_FEATURE_COLUMNS
                )
                .to_numpy()
            )

            current_home_probability = (
                model.predict_proba(
                    current_model_input
                )[0][1]
            )

            # ----------------------------------------------------
            # EARLY-SEASON BLENDING
            # ----------------------------------------------------

            current_weight = min(
                minimum_games_played / 4,
                1.0
            )

            prior_weight = (
                1.0 - current_weight
            )

            home_probability = (
                prior_home_probability * prior_weight +
                current_home_probability * current_weight
            )

            # ----------------------------------------------------
            # DATA SOURCE LABEL
            # ----------------------------------------------------

            if current_weight >= 1.0:

                data_source = (
                    f"{request.season} season data"
                )

            else:

                prior_percent = round(
                    prior_weight * 100
                )

                current_percent = round(
                    current_weight * 100
                )

                data_source = (
                    f"{prior_percent}% "
                    f"{prior_season} priors + "
                    f"{current_percent}% "
                    f"{request.season} season data"
                )

    # ------------------------------------------------------------
    # FINAL PREDICTION
    # ------------------------------------------------------------

    away_probability = (
        1 - home_probability
    )

    if home_probability >= 0.5:

        predicted_winner = (
            home_team
        )

    else:

        predicted_winner = (
            away_team
        )

    # ------------------------------------------------------------
    # LOG DATA SOURCE
    # ------------------------------------------------------------

    print(
        f"Prediction: {away_team} @ {home_team} | "
        f"Week {request.week}, {request.season} | "
        f"Data source: {data_source}"
    )

    # ------------------------------------------------------------
    # RESPONSE
    # ------------------------------------------------------------

    return {

        "season":
            request.season,

        "week":
            request.week,

        "away_team":
            away_team,

        "home_team":
            home_team,

        "away_probability":
            round(
                away_probability * 100,
                1
            ),

        "home_probability":
            round(
                home_probability * 100,
                1
            ),

        "predicted_winner":
            predicted_winner,

        "data_source":
            data_source
    }