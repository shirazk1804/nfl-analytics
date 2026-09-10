import polars as pl

from data import load_nfl_data

from model_io import (
    save_model
)

from display import (
    display_regular_season,
    display_playoffs,
    display_team_stats,
    display_passing_stats,
    display_rushing_stats,
    display_receiving_stats,
    display_offensive_stats,
    display_defensive_stats,
    display_team_rankings,
    display_team_comparison,
    display_matchup_prediction,
    display_ml_dataset_sample,
    display_ml_predictions
)

from stats import (
    get_team_games,
    calculate_record,
    calculate_team_stats,
    calculate_offensive_stats,
    calculate_passing_stats,
    calculate_rushing_stats,
    calculate_receiving_stats,
    calculate_defensive_stats,
    calculate_team_rankings
)

from backtest import (
    backtest_team_predictions,
    backtest_all_predictions
)

from prediction import calculate_matchup_prediction

from ml import (
    build_ml_dataset,
    build_multi_season_ml_dataset,
    train_ml_model,
    train_ensemble_model,
    evaluate_models_by_season
)

# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("NFL Analytics Platform")
    print("----------------------")

    # Get team and season from the user
    team = input("Enter an NFL team abbreviation: ").upper()
    season = int(input("Enter a season: "))

    print(f"\nLoading {season} {team} data...")

    games, pbp = load_nfl_data(season)

    # ------------------------------------------------------------
    # PREPARE TEAM DATA
    # ------------------------------------------------------------

    team_games = get_team_games(games, team)

    regular_season_games = team_games.filter(
        team_games["game_type"] == "REG"
    )

    playoff_games = team_games.filter(
        team_games["game_type"] != "REG"
    )

    # ------------------------------------------------------------
    # REGULAR SEASON
    # ------------------------------------------------------------

    wins, losses, ties = calculate_record(
        regular_season_games,
        team
    )

    display_regular_season(
        regular_season_games,
        team
    )

    print(f"\nRegular Season Record: {wins}-{losses}-{ties}")

    # ------------------------------------------------------------
    # PLAYOFFS
    # ------------------------------------------------------------

    display_playoffs(
        playoff_games,
        team
    )

    # ------------------------------------------------------------
    # TEAM STATS
    # ------------------------------------------------------------

    stats = calculate_team_stats(
        regular_season_games,
        team,
        wins,
        ties
    )

    display_team_stats(stats)

    # ------------------------------------------------------------
    # NFL TEAM RANKINGS
    # ------------------------------------------------------------

    all_team_stats = calculate_team_rankings(
        games,
        pbp
    )

    display_team_rankings(
        all_team_stats,
        team
    )

    # ------------------------------------------------------------
    # OFFENSIVE STATS
    # ------------------------------------------------------------

    games_played = len(regular_season_games)

    offensive_stats = calculate_offensive_stats(
        pbp,
        team,
        games_played
    )

    display_offensive_stats(offensive_stats)

    # ------------------------------------------------------------
    # PLAYER STATS
    # ------------------------------------------------------------

    passing_stats = calculate_passing_stats(
        pbp,
        team
    )

    display_passing_stats(passing_stats)

    rushing_stats = calculate_rushing_stats(
        pbp,
        team
    )

    display_rushing_stats(rushing_stats)

    receiving_stats = calculate_receiving_stats(
        pbp,
        team
    )

    display_receiving_stats(receiving_stats)

    # ------------------------------------------------------------
    # DEFENSIVE STATS
    # ------------------------------------------------------------

    defensive_stats = calculate_defensive_stats(
        pbp,
        team,
        games_played
    )

    display_defensive_stats(defensive_stats)

    # ------------------------------------------------------------
    # TEAM COMPARISON
    # ------------------------------------------------------------

    comparison_team = input(
        "\nEnter another team to compare, or press Enter to skip: "
    ).upper()

    if comparison_team:
        display_team_comparison(
            all_team_stats,
            team,
            comparison_team
        )

        home_team = input(
            f"\nWhich team is home ({team}/{comparison_team})? "
        ).upper()

        prediction = calculate_matchup_prediction(
            all_team_stats,
            team,
            comparison_team,
            home_team
        )

        display_matchup_prediction(
            prediction,
            team,
            comparison_team
        )

    backtest_team_predictions(
        games,
        pbp,
        team
    )

    heuristic_correct, heuristic_total, heuristic_accuracy = (
        backtest_all_predictions(
            games,
            pbp
        )
    )

    ml_dataset = build_ml_dataset(
        games,
        pbp,
        season
    )

    ml_df = pl.DataFrame(ml_dataset)

    ml_df.write_csv(
        f"ml_dataset_{season}.csv"
    )

    print(
        f"\nML dataset saved as "
        f"ml_dataset_{season}.csv"
    )

    display_ml_dataset_sample(ml_dataset)

    print("\nBUILDING MULTI-SEASON TRAINING DATASET")
    print("--------------------------------------")

    training_dataset = build_multi_season_ml_dataset(
        2021,
        2024
    )

    training_df = pl.DataFrame(training_dataset)

    training_df.write_csv(
        "ml_training_2021_2024.csv"
    )

    print("\nTRAINING DATASET")
    print("----------------")
    print(f"Total Rows: {len(training_dataset)}")

    print(
        "\nTraining dataset saved as "
        "ml_training_2021_2024.csv"
    )

    print("\nTRAINING MACHINE LEARNING MODEL")
    print("-------------------------------")

    (
        ml_model,
        ml_accuracy,
        ml_correct,
        ml_total,
        ml_predictions,
        ml_probabilities
    ) = train_ml_model(
        training_dataset,
        ml_dataset
    )
    

    print(f"Games Predicted: {ml_total}")

    print(f"Correct: {ml_correct}")

    print(f"Incorrect: {ml_total - ml_correct}")

    print(
        f"2025 Final Test Accuracy: "
        f"{ml_accuracy * 100:.1f}%"
    )

    print("\nTRAINING ENSEMBLE MODEL")
    print("-----------------------")

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
        ml_dataset
    )

    print("\n2025 TEST MODEL COMPARISON")
    print("----------------")

    # print(
    #   f"Heuristic: "
    #   f"{heuristic_correct}/{heuristic_total} "
    #   f"({heuristic_accuracy:.1f}%)"
    #)

    print(
        f"Logistic Regression: "
        f"{ml_correct}/{ml_total} "
        f"({ml_accuracy * 100:.1f}%)"
    )

    print(
        f"Decision Tree: "
        f"{dt_correct}/{ensemble_total} "
        f"({dt_accuracy * 100:.1f}%)"
    )

    print(
        f"Random Forest: "
        f"{rf_correct}/{ensemble_total} "
        f"({rf_accuracy * 100:.1f}%)"
    )

    print(
        f"XGBoost: "
        f"{xgb_correct}/{ensemble_total} "
        f"({xgb_accuracy * 100:.1f}%)"
    )

    print(
        f"Ensemble: "
        f"{ensemble_correct}/{ensemble_total} "
        f"({ensemble_accuracy * 100:.1f}%)"
    )

    print("\nROLLING MODEL EVALUATION")
    print("========================")

    rolling_results = evaluate_models_by_season()

    print("\nROLLING EVALUATION RESULTS")
    print("==========================")

    for result in rolling_results:

        print(f"\n{result['season']}")
        print("-" * 20)

        print(
            f"Logistic Regression: "
            f"{result['logistic_correct']}/"
            f"{result['logistic_total']} "
            f"({result['logistic_accuracy'] * 100:.1f}%)"
        )

        print(
            f"Decision Tree: "
            f"{result['decision_tree_correct']}/"
            f"{result['logistic_total']} "
            f"({result['decision_tree_accuracy'] * 100:.1f}%)"
        )

        print(
            f"Random Forest: "
            f"{result['random_forest_correct']}/"
            f"{result['logistic_total']} "
            f"({result['random_forest_accuracy'] * 100:.1f}%)"
        )

        print(
            f"XGBoost: "
            f"{result['xgboost_correct']}/"
            f"{result['logistic_total']} "
            f"({result['xgboost_accuracy'] * 100:.1f}%)"
        )

        print(
            f"Ensemble: "
            f"{result['ensemble_correct']}/"
            f"{result['logistic_total']} "
            f"({result['ensemble_accuracy'] * 100:.1f}%)"
        )

    display_ml_predictions(
    ml_dataset,
    ml_predictions,
    ml_probabilities
    )

if __name__ == "__main__":
    main()

