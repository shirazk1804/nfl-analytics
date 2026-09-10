from ml import (
    LOGISTIC_FEATURE_COLUMNS,
    build_matchup_features,
    build_prior_season_matchup_features
)

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from model_io import load_model

import nflreadpy as nfl
import polars as pl


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

        matchups.append({
            "away_team":
                game["away_team"],

            "home_team":
                game["home_team"],

            "gameday":
                str(game["gameday"])
        })

    return {
        "season": season,
        "week": week,
        "games": matchups
    }


# ============================================================
# GAME PREDICTION
# ============================================================

@app.post("/predict")
def predict_game(
    request: PredictionRequest
):

    home_team = (
        request.home_team.upper()
    )

    away_team = (
        request.away_team.upper()
    )

    # ------------------------------------------------------------
    # LOAD SCHEDULE
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

    current_game_date = (
        game["gameday"]
    )

    # ------------------------------------------------------------
    # DECIDE WHICH SEASON DATA TO USE
    # ------------------------------------------------------------

    use_prior_season = False

    # Week 1 always uses last season
    if request.week == 1:

        use_prior_season = True

    else:

        try:

            pbp = get_pbp(
                request.season
            )

            # Completed games before the selected week
            completed_games = regular_games.filter(
                (pl.col("week") < request.week) &
                pl.col("home_score").is_not_null() &
                pl.col("away_score").is_not_null()
            )

            teams_that_played = set()

            for completed_game in completed_games.iter_rows(
                named=True
            ):

                teams_that_played.add(
                    completed_game["home_team"]
                )

                teams_that_played.add(
                    completed_game["away_team"]
                )

            # Only use current-season stats if BOTH teams
            # have already played a completed game
            if (
                home_team not in teams_that_played or
                away_team not in teams_that_played
            ):

                use_prior_season = True

        except ValueError:

            use_prior_season = True

    # ------------------------------------------------------------
    # BUILD FEATURES
    # ------------------------------------------------------------

    try:

        if use_prior_season:

            prior_season = (
                request.season - 1
            )

            prior_games = get_schedule(
                prior_season
            )

            prior_pbp = get_pbp(
                prior_season
            )

            features = (
                build_prior_season_matchup_features(
                    games=prior_games,
                    pbp=prior_pbp,
                    season=prior_season,
                    home_team=home_team,
                    away_team=away_team
                )
            )

            data_source = (
                f"{prior_season} season priors"
            )

        else:

            features = build_matchup_features(
                games=games,
                pbp=pbp,
                season=request.season,
                week=request.week,
                home_team=home_team,
                away_team=away_team,
                current_game_date=current_game_date
            )

            data_source = (
                f"{request.season} season data"
            )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    # ------------------------------------------------------------
    # MODEL INPUT
    # ------------------------------------------------------------

    feature_row = pl.DataFrame(
        [features]
    )

    game_features = (
        feature_row
        .select(
            LOGISTIC_FEATURE_COLUMNS
        )
        .to_numpy()
    )

    # ------------------------------------------------------------
    # PREDICTION
    # ------------------------------------------------------------

    home_probability = (
        model.predict_proba(
            game_features
        )[0][1]
    )

    away_probability = (
        1 -
        home_probability
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