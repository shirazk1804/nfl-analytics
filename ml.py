# ============================================================
# MACHINE LEARNING
# ============================================================

import nflreadpy as nfl
import polars as pl

from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.ensemble import (
    RandomForestClassifier,
    VotingClassifier
)

from stats import (
    calculate_team_rankings,
    calculate_recent_form,
    calculate_elo_ratings,
    calculate_rest_features,
    calculate_qb_features
)

# ============================================================
# LOGISTIC REGRESSION FEATURES
# ============================================================

LOGISTIC_FEATURE_COLUMNS = [
    "home_points_per_game",
    "away_points_per_game",
    "home_points_allowed_per_game",
    "away_points_allowed_per_game",
    "home_yards_per_game",
    "away_yards_per_game",
    "home_passing_yards_per_attempt",
    "away_passing_yards_per_attempt",
    "home_rushing_yards_per_attempt",
    "away_rushing_yards_per_attempt",
    "home_yards_allowed_per_game",
    "away_yards_allowed_per_game",
    "home_turnover_diff_per_game",
    "away_turnover_diff_per_game",
    "home_win_percentage",
    "away_win_percentage",
    "home_yards_per_play",
    "away_yards_per_play",
    "home_yards_allowed_per_play",
    "away_yards_allowed_per_play",
    "home_recent_points_per_game",
    "away_recent_points_per_game",
    "home_recent_points_allowed_per_game",
    "away_recent_points_allowed_per_game",
    "home_recent_win_percentage",
    "away_recent_win_percentage",
    "home_offensive_epa_per_play",
    "away_offensive_epa_per_play",
    "home_defensive_epa_per_play",
    "away_defensive_epa_per_play",
    "home_special_teams_epa_per_play",
    "away_special_teams_epa_per_play",
    "home_elo",
    "away_elo",
    "elo_difference",
    "home_days_rest",
    "away_days_rest",
    "rest_difference",
    "home_after_bye",
    "away_after_bye"
]

# ============================================================
# CROSS SEASON ELO
# ============================================================

def build_season_start_elo(
        season,
        base_rating=1500,
        k_factor=20,
        carryover=0.67,
        first_history_season=2020
):

    ratings = {}

    for current_season in range(
        first_history_season,
        season
    ):
        season_games = nfl.load_schedules(
            current_season
        )

# ============================================================
# MATCHUP FEATURE BUILDER
# ============================================================

def build_matchup_features(
    games,
    pbp,
    season,
    week,
    home_team,
    away_team,
    current_game_date
):

    home_team = home_team.upper()
    away_team = away_team.upper()

    if week < 2:

        raise ValueError(
            "Predictions currently require Week 2 or later."
        )

    # ------------------------------------------------------------
    # PREVIOUS GAMES
    # ------------------------------------------------------------

    regular_games = games.filter(
        games["game_type"] == "REG"
    )

    previous_games = regular_games.filter(
        (pl.col("week") < week) &
        pl.col("home_score").is_not_null() &
        pl.col("away_score").is_not_null()
    )

    previous_pbp = pbp.filter(
        (pbp["season_type"] == "REG") &
        (pbp["week"] < week)
    )

    # ------------------------------------------------------------
    # TEAM STATS
    # ------------------------------------------------------------

    all_team_stats = calculate_team_rankings(
        previous_games,
        previous_pbp
    )

    home_stats = next(
        (
            stats
            for stats in all_team_stats
            if stats["team"] == home_team
        ),
        None
    )

    away_stats = next(
        (
            stats
            for stats in all_team_stats
            if stats["team"] == away_team
        ),
        None
    )

    if home_stats is None:

        raise ValueError(
            f"No previous stats found for {home_team}."
        )

    if away_stats is None:

        raise ValueError(
            f"No previous stats found for {away_team}."
        )

    # ------------------------------------------------------------
    # RECENT FORM
    # ------------------------------------------------------------

    home_recent = calculate_recent_form(
        previous_games,
        home_team
    )

    away_recent = calculate_recent_form(
        previous_games,
        away_team
    )

    # ------------------------------------------------------------
    # ELO
    # ------------------------------------------------------------

    elo_ratings = calculate_elo_ratings(
        previous_games
    )

    home_elo = elo_ratings.get(
        home_team,
        1500.0
    )

    away_elo = elo_ratings.get(
        away_team,
        1500.0
    )

    elo_difference = (
        home_elo -
        away_elo
    )

    # ------------------------------------------------------------
    # REST / BYE
    # ------------------------------------------------------------

    home_rest = calculate_rest_features(
        previous_games,
        home_team,
        current_game_date,
        week
    )

    away_rest = calculate_rest_features(
        previous_games,
        away_team,
        current_game_date,
        week
    )

    rest_difference = (
        home_rest["days_rest"] -
        away_rest["days_rest"]
    )

    # ------------------------------------------------------------
    # LOGISTIC REGRESSION FEATURES
    # ------------------------------------------------------------

    features = {

        "home_points_per_game":
            home_stats["points_per_game"],

        "away_points_per_game":
            away_stats["points_per_game"],

        "home_points_allowed_per_game":
            home_stats["points_allowed_per_game"],

        "away_points_allowed_per_game":
            away_stats["points_allowed_per_game"],

        "home_yards_per_game":
            home_stats["total_yards_per_game"],

        "away_yards_per_game":
            away_stats["total_yards_per_game"],

        "home_passing_yards_per_attempt":
            home_stats["passing_yards_per_attempt"],

        "away_passing_yards_per_attempt":
            away_stats["passing_yards_per_attempt"],

        "home_rushing_yards_per_attempt":
            home_stats["rushing_yards_per_attempt"],

        "away_rushing_yards_per_attempt":
            away_stats["rushing_yards_per_attempt"],

        "home_yards_allowed_per_game":
            home_stats["yards_allowed_per_game"],

        "away_yards_allowed_per_game":
            away_stats["yards_allowed_per_game"],

        "home_turnover_diff_per_game":
            (
                home_stats["turnover_differential"] /
                home_stats["games_played"]
            ),

        "away_turnover_diff_per_game":
            (
                away_stats["turnover_differential"] /
                away_stats["games_played"]
            ),

        "home_win_percentage":
            home_stats["win_percentage"],

        "away_win_percentage":
            away_stats["win_percentage"],

        "home_yards_per_play":
            home_stats["yards_per_play"],

        "away_yards_per_play":
            away_stats["yards_per_play"],

        "home_yards_allowed_per_play":
            home_stats["yards_allowed_per_play"],

        "away_yards_allowed_per_play":
            away_stats["yards_allowed_per_play"],

        "home_recent_points_per_game":
            home_recent["points_per_game"],

        "away_recent_points_per_game":
            away_recent["points_per_game"],

        "home_recent_points_allowed_per_game":
            home_recent["points_allowed_per_game"],

        "away_recent_points_allowed_per_game":
            away_recent["points_allowed_per_game"],

        "home_recent_win_percentage":
            home_recent["win_percentage"],

        "away_recent_win_percentage":
            away_recent["win_percentage"],

        "home_offensive_epa_per_play":
            home_stats["offensive_epa_per_play"],

        "away_offensive_epa_per_play":
            away_stats["offensive_epa_per_play"],

        "home_defensive_epa_per_play":
            home_stats["defensive_epa_per_play"],

        "away_defensive_epa_per_play":
            away_stats["defensive_epa_per_play"],

        "home_special_teams_epa_per_play":
            home_stats["special_teams_epa_per_play"],

        "away_special_teams_epa_per_play":
            away_stats["special_teams_epa_per_play"],

        "home_elo":
            home_elo,

        "away_elo":
            away_elo,

        "elo_difference":
            elo_difference,

        "home_days_rest":
            home_rest["days_rest"],

        "away_days_rest":
            away_rest["days_rest"],

        "rest_difference":
            rest_difference,

        "home_after_bye":
            home_rest["after_bye"],

        "away_after_bye":
            away_rest["after_bye"]
    }

    return features

# ============================================================
# PRIOR-SEASON MATCHUP FEATURES
# ============================================================

def build_prior_season_matchup_features(
    games,
    pbp,
    season,
    home_team,
    away_team
):

    regular_games = games.filter(
        games["game_type"] == "REG"
    )

    # Use a date from the end of the season.
    # Rest features will be replaced with neutral values below.
    last_game = (
        regular_games
        .sort("gameday")
        .tail(1)
        .row(
            0,
            named=True
        )
    )

    last_game_date = (
        last_game["gameday"]
    )

    # Week 19 makes the existing feature builder
    # use all Weeks 1-18 from the previous season.
    features = build_matchup_features(
        games=games,
        pbp=pbp,
        season=season,
        week=19,
        home_team=home_team,
        away_team=away_team,
        current_game_date=last_game_date
    )

    # Rest from January to September would not make
    # sense, so use neutral rest values.
    features["home_days_rest"] = 7
    features["away_days_rest"] = 7
    features["rest_difference"] = 0

    features["home_after_bye"] = 0
    features["away_after_bye"] = 0

    return features

def build_ml_dataset(games, pbp, season, start_week=2):

    regular_games = games.filter(
        games["game_type"] == "REG"
    )

    dataset = []

    for week in range(start_week, 19):

        # Only use info available before this week
        previous_games = regular_games.filter(
            regular_games["week"] < week
        )

        elo_ratings = calculate_elo_ratings(
            previous_games
        )

        previous_pbp = pbp.filter(
            (pbp["season_type"] == "REG") &
            (pbp["week"] < week)
        )

        all_team_stats = calculate_team_rankings(
            previous_games,
            previous_pbp
        )

        week_games = regular_games.filter(
            regular_games["week"] == week
        )

        for game in week_games.iter_rows(named=True):
            
            home_team = game["home_team"]
            away_team = game["away_team"]

            current_game_date = game["gameday"]

            home_rest = calculate_rest_features(
                previous_games,
                home_team,
                current_game_date,
                week
            )

            away_rest = calculate_rest_features(
                previous_games,
                away_team,
                current_game_date,
                week
            )

            rest_difference = (
                home_rest["days_rest"] - away_rest["days_rest"]
            )

            home_elo = elo_ratings.get(
                home_team,
                1500.0
            )

            away_elo = elo_ratings.get(
                away_team,
                1500.0
            )

            elo_difference = (home_elo - away_elo)

            home_stats = next(
                stats for stats in all_team_stats
                if stats["team"] == home_team
            )

            away_stats = next(
                stats for stats in all_team_stats
                if stats["team"] == away_team
            )

            home_recent = calculate_recent_form(
                previous_games,
                home_team
            )

            away_recent = calculate_recent_form(
                previous_games,
                away_team
            )

            home_qb = calculate_qb_features(
                previous_pbp,
                home_team
            )

            away_qb = calculate_qb_features(
                previous_pbp,
                away_team
            )

            home_score = game["home_score"]
            away_score = game["away_score"]

            # Skip games without final score
            if home_score is None or away_score is None:
                continue

            # Skip ties for this first prediction model
            if home_score == away_score:
                continue

            # 1 = home team won
            # 0 = away team won
            home_win = 1 if home_score > away_score else 0

            dataset.append({
                "season": season,
                "week": week,
                "home_team": home_team,
                "away_team": away_team,

                "home_elo": home_elo,
                "away_elo": away_elo,
                "elo_difference": elo_difference,

                "home_days_rest":
                    home_rest["days_rest"],

                "away_days_rest":
                    away_rest["days_rest"],

                "rest_difference":
                    rest_difference,

                "home_after_bye":
                    home_rest["after_bye"],

                "away_after_bye":
                    away_rest["after_bye"],

                "home_points_per_game":
                    home_stats["points_per_game"],
                
                "away_points_per_game":
                    away_stats["points_per_game"],

                "home_points_allowed_per_game":
                    home_stats["points_allowed_per_game"],

                "away_points_allowed_per_game":
                    away_stats["points_allowed_per_game"],
                
                "home_yards_per_game":
                    home_stats["total_yards_per_game"],

                "away_yards_per_game":
                    away_stats["total_yards_per_game"],
                
                "home_passing_yards_per_attempt":
                    home_stats["passing_yards_per_attempt"],
                
                "away_passing_yards_per_attempt":
                    away_stats["passing_yards_per_attempt"],
                
                "home_rushing_yards_per_attempt":
                    home_stats["rushing_yards_per_attempt"],
                
                "away_rushing_yards_per_attempt":
                    away_stats["rushing_yards_per_attempt"],
                
                "home_offensive_epa_per_play":
                    home_stats["offensive_epa_per_play"],
                
                "away_offensive_epa_per_play":
                    away_stats["offensive_epa_per_play"],

                "home_yards_allowed_per_game":
                    home_stats["yards_allowed_per_game"],

                "away_yards_allowed_per_game":
                    away_stats["yards_allowed_per_game"],

                "home_turnover_diff_per_game":
                    home_stats["turnover_differential"]
                    / home_stats["games_played"],

                "away_turnover_diff_per_game":
                    away_stats["turnover_differential"]
                    / away_stats["games_played"],
                
                "home_win_percentage":
                    home_stats["win_percentage"],

                "away_win_percentage":
                    away_stats["win_percentage"],
                
                "home_yards_per_play":
                    home_stats["yards_per_play"],
                
                "away_yards_per_play":
                    away_stats["yards_per_play"],
                
                "home_yards_allowed_per_play":
                    home_stats["yards_allowed_per_play"],
                
                "away_yards_allowed_per_play":
                    away_stats["yards_allowed_per_play"],
                
                "home_defensive_epa_per_play":
                    home_stats["defensive_epa_per_play"],
                
                "away_defensive_epa_per_play":
                    away_stats["defensive_epa_per_play"],
                
                "home_recent_points_per_game":
                    home_recent["points_per_game"],
                
                "away_recent_points_per_game":
                    away_recent["points_per_game"],
 
                "home_recent_points_allowed_per_game":
                    home_recent["points_allowed_per_game"],

                "away_recent_points_allowed_per_game":
                    away_recent["points_allowed_per_game"],
                
                "home_special_teams_epa_per_play":
                    home_stats["special_teams_epa_per_play"],
                
                "away_special_teams_epa_per_play":
                    away_stats["special_teams_epa_per_play"],

                "home_recent_win_percentage":
                    home_recent["win_percentage"],

                "away_recent_win_percentage":
                    away_recent["win_percentage"],
                
                "home_offensive_success_rate":
                    home_stats["offensive_success_rate"],

                "away_offensive_success_rate":
                    away_stats["offensive_success_rate"],

                "home_defensive_success_rate":
                    home_stats["defensive_success_rate"],

                "away_defensive_success_rate":
                    away_stats["defensive_success_rate"],

                "home_qb_epa_per_play":
                    home_qb["qb_epa_per_play"],

                "away_qb_epa_per_play":
                    away_qb["qb_epa_per_play"],

                "home_qb_yards_per_attempt":
                    home_qb["qb_yards_per_attempt"],

                "away_qb_yards_per_attempt":
                    away_qb["qb_yards_per_attempt"],

                "home_qb_td_rate":
                    home_qb["qb_td_rate"],

                "away_qb_td_rate":
                    away_qb["qb_td_rate"],

                "home_qb_interception_rate":
                    home_qb["qb_interception_rate"],

                "away_qb_interception_rate":
                    away_qb["qb_interception_rate"],

                "home_win": home_win
            })

    return dataset

def build_multi_season_ml_dataset(start_season, end_season):
    combined_dataset = []

    for current_season in range(start_season, end_season + 1):
        print(f"\nLoading {current_season} data for ML dataset...")

        season_games = nfl.load_schedules(current_season)
        season_pbp = nfl.load_pbp(current_season)

        season_dataset = build_ml_dataset(
            season_games,
            season_pbp,
            current_season
        )

        combined_dataset.extend(season_dataset)

        print(
            f"{current_season}: "
            f"{len(season_dataset)} rows added"
        )
    return combined_dataset

def train_ml_model(training_dataset, test_dataset):

    feature_columns = LOGISTIC_FEATURE_COLUMNS

    training_df = pl.DataFrame(training_dataset)
    test_df = pl.DataFrame(test_dataset)

    # Training inputs
    X_train = training_df.select(
        feature_columns
    ).to_numpy()

    # Training answers
    y_train = training_df[
        "home_win"
    ].to_numpy()

    # 2025 inputs
    X_test = test_df.select(
        feature_columns
    ).to_numpy()

    # Actual 2025 results
    y_test = test_df[
        "home_win"
    ].to_numpy()

    # Create the machine-learning model
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(
            max_iter=1000
        )
    )

    # Learn from 2021-2024
    model.fit(
        X_train,
        y_train
    )

    # Predict 2025
    predictions = model.predict(
        X_test
    )

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    correct = (predictions == y_test).sum()
    total = len(y_test)

    return model, accuracy, correct, total, predictions, probabilities

# ============================================================
# PRODUCTION LOGISTIC REGRESSION MODEL
# ============================================================

def train_production_model(
    training_dataset
):

    training_df = pl.DataFrame(
        training_dataset
    )

    X_train = training_df.select(
        LOGISTIC_FEATURE_COLUMNS
    ).to_numpy()

    y_train = training_df[
        "home_win"
    ].to_numpy()

    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(
            max_iter=1000
        )
    )

    model.fit(
        X_train,
        y_train
    )

    return model

# ============================================================
# ENSEMBLE ML MODEL
# ============================================================

def train_ensemble_model(
        training_dataset,
        test_dataset
):
    feature_columns = [
        "home_points_per_game",
        "away_points_per_game",
        "home_points_allowed_per_game",
        "away_points_allowed_per_game",
        "home_yards_per_game",
        "away_yards_per_game",
        "home_passing_yards_per_attempt",
        "away_passing_yards_per_attempt",
        "home_rushing_yards_per_attempt",
        "away_rushing_yards_per_attempt",
        "home_yards_allowed_per_game",
        "away_yards_allowed_per_game",
        "home_turnover_diff_per_game",
        "away_turnover_diff_per_game",
        "home_win_percentage",
        "away_win_percentage",
        "home_yards_per_play",
        "away_yards_per_play",
        "home_yards_allowed_per_play",
        "away_yards_allowed_per_play",
        "home_recent_points_per_game",
        "away_recent_points_per_game",
        "home_recent_points_allowed_per_game",
        "away_recent_points_allowed_per_game",
        "home_recent_win_percentage",
        "away_recent_win_percentage",
        "home_offensive_epa_per_play",
        "away_offensive_epa_per_play",
        "home_defensive_epa_per_play",
        "away_defensive_epa_per_play",
        "home_special_teams_epa_per_play",
        "away_special_teams_epa_per_play",
        "home_elo",
        "away_elo",
        "elo_difference"
    ]

    training_df = pl.DataFrame(
        training_dataset
    )

    test_df = pl.DataFrame(
        test_dataset
    )

    X_train = training_df.select(
        feature_columns
    ).to_numpy()

    y_train = training_df[
        "home_win"
    ].to_numpy()

    X_test = test_df.select(
        feature_columns
    ).to_numpy()

    y_test = test_df[
        "home_win"
    ].to_numpy()

    # Logistic Regression
    logistic_model = make_pipeline(
        StandardScaler(),
        LogisticRegression(
            max_iter=1000
        )
    )

    # Random Forest
    random_forest_model = RandomForestClassifier(
        n_estimators=300,
        max_depth=6,
        random_state=42
    )

    decision_tree_model = DecisionTreeClassifier(
        max_depth=5,
        random_state=42
    )

    xgboost_model = XGBClassifier(
        n_estimators=300,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="logloss"
    )

    # Combine Models
    ensemble_model = VotingClassifier(
        estimators=[
            ("logistic", logistic_model),
            ("random_forest", random_forest_model),
            ("xgboost", xgboost_model)
        ],
        voting="soft"
    )

    # Train model
    print("Training Ensemble...")
    ensemble_model.fit(
        X_train,
        y_train
    )

    print("Training Decision Tree...")
    decision_tree_model.fit(
        X_train,
        y_train
    )

    dt_predictions = decision_tree_model.predict(
        X_test
    )

    dt_accuracy = accuracy_score(
        y_test,
        dt_predictions
    )

    dt_correct = (
        dt_predictions == y_test
    ).sum()

    print("Training XGBoost...")
    xgboost_model.fit(
        X_train,
        y_train
    )

    xgb_predictions = xgboost_model.predict(
        X_test
    )

    xgb_accuracy = accuracy_score(
        y_test,
        xgb_predictions
    )

    xgb_correct = (
        xgb_predictions == y_test
    ).sum()

    random_forest = ensemble_model.named_estimators_[
        "random_forest"
    ]

    rf_predictions = random_forest.predict(
        X_test
    )

    rf_accuracy = accuracy_score(
        y_test,
        rf_predictions
    )

    rf_correct = (
        rf_predictions == y_test
    ).sum()

    # Predict 2025 Games
    predictions = ensemble_model.predict(
        X_test
    )

    probabilities = ensemble_model.predict_proba(
        X_test
    )[:, 1]

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    correct = (
        predictions == y_test
    ).sum()

    total = len(y_test)

    return(
        ensemble_model,
        accuracy,
        correct,
        total,
        predictions,
        probabilities,
        rf_accuracy,
        rf_correct,
        dt_accuracy,
        dt_correct,
        xgb_accuracy,
        xgb_correct
    )

# ============================================================
# ROLLING MODEL EVALUATION
# ============================================================

def evaluate_models_by_season(
        start_training_season=2021,
        test_seasons=(2023, 2024, 2025)
):
    results = []

    for test_season in test_seasons:

        print(
            f"\nROLLING EVALUATION: {test_season}"
        )
        print("------------------------")

        training_end_season = test_season - 1

        print(
            f"Training: "
            f"{start_training_season}-"
            f"{training_end_season}"
        )

        print(
            f"Testing: {test_season}"
        )

        # Build Training Data
        training_dataset = (
            build_multi_season_ml_dataset(
                start_training_season,
                training_end_season
            )
        )

        # Build Test Data
        test_games = nfl.load_schedules(
            test_season
        )

        test_pbp = nfl.load_pbp(
            test_season
        )

        test_dataset = build_ml_dataset(
            test_games,
            test_pbp,
            test_season
        )

        # Logistic Regression
        (
            logistic_model,
            logistic_accuracy,
            logistic_correct,
            logistic_total,
            logistic_predictions,
            logistic_probabilities
        ) = train_ml_model(
            training_dataset,
            test_dataset
        )

        # Other models + Ensemble
        (
            ensemble_model,
            ensemble_accuracy,
            ensemble_correct,
            ensemble_total,
            ensemble_predictions,
            ensemble_probabilities,
            rf_accuracy,
            rf_correct,
            dt_accuracy,
            dt_correct,
            xgb_accuracy,
            xgb_correct
        ) = train_ensemble_model(
            training_dataset,
            test_dataset
        )

        results.append({
            "season": test_season,

            "logistic_correct": logistic_correct,

            "logistic_total": logistic_total,

            "logistic_accuracy": logistic_accuracy,

            "decision_tree_correct": dt_correct,

            "decision_tree_accuracy": dt_accuracy,

            "random_forest_correct": rf_correct,

            "random_forest_accuracy": rf_accuracy,

            "xgboost_correct": xgb_correct,

            "xgboost_accuracy": xgb_accuracy,

            "ensemble_correct": ensemble_correct,

            "ensemble_accuracy": ensemble_accuracy
        })

    return results