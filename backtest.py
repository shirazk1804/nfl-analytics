# ============================================================
# BACKTESTING
# ============================================================

from stats import (
    get_team_games,
    calculate_team_rankings
)

from prediction import calculate_matchup_prediction

def backtest_team_predictions(games, pbp, team, start_week=2):
    regular_games = games.filter(
        games["game_type"] == "REG"
    )

    team_games = get_team_games(
        regular_games,
        team
    )

    correct = 0
    incorrect = 0

    print("\nPREDICTION BACKTEST")
    print("-------------------")

    for game in team_games.iter_rows(named=True):
        week = game["week"]

        if week < start_week:
            continue

        # Only use games that happened before this week
        previous_games = regular_games.filter(
            regular_games["week"] < week
        )

        previous_pbp = pbp.filter(
            (pbp["season_type"] == "REG") &
            (pbp["week"] < week)
        )

        # Get team stats using only prior weeks
        all_team_stats = calculate_team_rankings(
            previous_games,
            previous_pbp
        )

        home_team = game["home_team"]
        away_team = game["away_team"]

        prediction = calculate_matchup_prediction(
            all_team_stats,
            away_team,
            home_team,
            home_team
        )

        away_projected = prediction["team1_projected_points"]
        home_projected = prediction["team2_projected_points"]

        # Determine predicted winner
        if home_projected > away_projected:
            predicted_winner = home_team
        elif away_projected > home_projected:
            predicted_winner = away_team
        else:
            predicted_winner = "Tie"
        
        home_score = game["home_score"]
        away_score = game["away_score"]
        
        # Skip games without final score
        if home_score is None or away_score is None:
            continue

        # Determine actual winner
        if home_score > away_score:
            actual_winner = home_team
        elif away_score > home_score:
            actual_winner = away_team
        else:
            actual_winner = "Tie"
        
        if predicted_winner == actual_winner:
            result = "CORRECT"
            correct += 1
        else:
            result = "WRONG"
            incorrect += 1
        
        print(
            f"Week {week}: "
            f"{away_team} @ {home_team} | "
            f"Prediction: {predicted_winner} | "
            f"Actual: {actual_winner} | "
            f"{result}"
        ) 

    total_predictions = correct + incorrect

    print("\nBACKTEST RESULTS")
    print("----------------")

    print(f"Correct: {correct}")
    print(f"Incorrect: {incorrect}")

    if total_predictions > 0:
        accuracy = (
            correct / total_predictions
        ) * 100

        print(f"Accuracy: {accuracy:.1f}%")

def backtest_all_predictions(games, pbp, start_week=2):
    regular_games = games.filter(
        games["game_type"] == "REG"
    )

    correct = 0
    incorrect = 0

    print("\nFULL NFL PREDICTION BACKTEST")
    print("----------------------------")

    for week in range(start_week, 19):
        
        # Only use info available before this week
        previous_games = regular_games.filter(
            regular_games["week"] < week
        )

        previous_pbp = pbp.filter(
            (pbp["season_type"] == "REG") &
            (pbp["week"] < week)
        )

        # Calculate league stats once for the entire week
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

            prediction = calculate_matchup_prediction(
                all_team_stats,
                away_team,
                home_team,
                home_team
            )

            away_projected = prediction[
                "team1_projected_points"
            ]

            home_projected = prediction[
                "team2_projected_points"
            ]

            # Predicted Winner
            if home_projected > away_projected:
                predicted_winner = home_team
            elif away_projected > home_projected:
                predicted_winner = away_team
            else:
                predicted_winner = "Tie"
            
            home_score = game["home_score"]
            away_score = game["away_score"]

            # Skip games without final scores
            if home_score is None or away_score is None:
                continue

            if home_score == away_score:
                continue

            # Actual winner
            if home_score > away_score:
                actual_winner = home_team
            elif away_score > home_score:
                actual_winner = away_team
            else:
                actual_winner = "Tie"
            
            if predicted_winner == actual_winner:
                correct += 1
                result = "CORRECT"
            else:
                incorrect += 1
                result = "WRONG"
            
            print(
                f"Week {week}: "
                f"{away_team} @ {home_team} | "
                f"Prediction: {predicted_winner} | "
                f"Actual: {actual_winner} | "
                f"{result}"
            )

    total_predictions = correct + incorrect

    print("\nFULL NFL BACKTEST RESULT")
    print("-------------------------")
    print(f"Games Predicted: {total_predictions}")
    print(f"Correct: {correct}")
    print(f"Incorrect: {incorrect}")

    if total_predictions > 0:
        accuracy = (
            correct / total_predictions
        ) * 100
        
    print(f"Accuracy: {accuracy:.1f}%")

    return correct, total_predictions, accuracy
