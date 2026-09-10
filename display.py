from stats import get_team_rank

# Displays every regular-season week, including the team's bye
def display_regular_season(regular_season_games, team):
    print("\nREGULAR SEASON")
    print("--------------")

    played_weeks = regular_season_games["week"].to_list()

    # NFL regular season runs from Week 1 through Week 18
    for week in range(1, 19):

        if week not in played_weeks:
            print(f"Week {week}: BYE")
            continue

        game = regular_season_games.filter(
            regular_season_games["week"] == week
        ).row(0, named=True)

        # Determine opponent and score based on home/away status
        if game["home_team"] == team:
            team_score = game["home_score"]
            opponent = game["away_team"]
            opponent_score = game["away_score"]
        else:
            team_score = game["away_score"]
            opponent = game["home_team"]
            opponent_score = game["home_score"]

        # Determine game result
        if team_score > opponent_score:
            result = "W"
        elif team_score < opponent_score:
            result = "L"
        else:
            result = "T"

        print(
            f"Week {week}: {result} vs {opponent} "
            f"{team_score}-{opponent_score}"
        )

# Displays playoff results using the actual playoff round names
def display_playoffs(playoff_games, team):
    print("\nPLAYOFFS")
    print("--------")

    playoff_rounds = {
        "WC": "Wild Card",
        "DIV": "Divisional Round",
        "CON": "Conference Championship",
        "SB": "Super Bowl"
    }

    if playoff_games.height == 0:
        print("Did not make playoffs")
        return

    for game in playoff_games.iter_rows(named=True):

        # Determine opponent and score
        if game["home_team"] == team:
            team_score = game["home_score"]
            opponent = game["away_team"]
            opponent_score = game["away_score"]
        else:
            team_score = game["away_score"]
            opponent = game["home_team"]
            opponent_score = game["home_score"]

        # Determine playoff game result
        if team_score > opponent_score:
            result = "W"
        elif team_score < opponent_score:
            result = "L"
        else:
            result = "T"

        round_name = playoff_rounds[game["game_type"]]

        print(
            f"{round_name}: {result} vs {opponent} "
            f"{team_score}-{opponent_score}"
        )

# Displays the calculated team statistics
def display_team_stats(stats):
    print("\nTEAM STATISTICS")
    print("---------------")

    print(f"Points Scored: {stats['points_scored']}")
    print(f"Points Allowed: {stats['points_allowed']}")
    print(f"Point Differential: {stats['point_differential']:+}")
    print(f"Points Per Game: {stats['points_per_game']:.1f}")
    print(f"Points Allowed Per Game: {stats['points_allowed_per_game']:.1f}")
    print(f"Win Percentage: {stats['win_percentage']:.1f}%")

    print(
        f"\nHome Record: "
        f"{stats['home_wins']}-{stats['home_losses']}-{stats['home_ties']}"
    )

    print(
        f"Away Record: "
        f"{stats['away_wins']}-{stats['away_losses']}-{stats['away_ties']}"
    )

# Displays single player passing stats
def display_passing_stats(passing_stats):
    print("\nPASSING")
    print("-------")

    for passer, stats in sorted(
        passing_stats.items(),
        key=lambda item: item[1]["yards"],
        reverse=True
    ):

        if stats["attempts"] > 0:
            completion_percentage = (
                stats["completions"] / stats["attempts"]
            ) * 100

            yards_per_attempt = (
                stats["yards"] / stats["attempts"]
            )
        else:
            completion_percentage = 0
            yards_per_attempt = 0

        print(f"\n{passer}")
        print(
            f"Completions/Attempts: "
            f"{stats['completions']}/{stats['attempts']}"
        )
        print(f"Completion %: {completion_percentage:.1f}%")
        print(f"Passing Yards: {stats['yards']:.0f}")
        print(f"Passing TDs: {stats['touchdowns']}")
        print(f"Interceptions: {stats['interceptions']}")
        print(f"Yards Per Attempt: {yards_per_attempt:.1f}")

# Displays Single Player Rushing Stats
def display_rushing_stats(rushing_stats):
    print("\nRUSHING")
    print("-------")

    for rusher, stats in sorted(
        rushing_stats.items(),
        key=lambda item: item[1]["yards"],
        reverse=True
    ):

        if stats["attempts"] > 0:
            yards_per_carry = stats["yards"] / stats["attempts"]
        else:
            yards_per_carry = 0
    
        print(f"\n{rusher}")
        print(f"Attempts: {stats['attempts']}")
        print(f"Rushing Yards: {stats['yards']:.0f}")
        print(f"Rushing TDs: {stats['touchdowns']}")
        print(f"Yards Per Carry: {yards_per_carry:.1f}")

# Displays Single Player Receiving Stats
def display_receiving_stats(receiving_stats):
    print("\nRECEIVING")
    print("---------")

    for receiver, stats in sorted(
        receiving_stats.items(),
        key=lambda item: item[1]["yards"],
        reverse=True
    ):

        if stats["receptions"] > 0:
            yards_per_reception = stats["yards"] / stats["receptions"]
        else:
            yards_per_reception = 0
        
        if stats["targets"] > 0:
            catch_percentage = (
                stats["receptions"] / stats["targets"]
            ) * 100
        else:
            catch_percentage = 0
        
        print(f"\n{receiver}")
        print(f"Targets: {stats['targets']}")
        print(f"Receptions: {stats['receptions']}")
        print(f"Receiving Yards: {stats['yards']:.0f}")
        print(f"Receiving TDs: {stats['touchdowns']}")
        print(f"Yards Per Reception: {yards_per_reception:.1f}")
        print(f"Catch Percentage: {catch_percentage:.1f}%")

# Displays offensive yardage statistics
def display_offensive_stats(stats):
    print("\nOFFENSIVE STATISTICS")
    print("--------------------")

    print(f"Total Yards: {stats['total_yards']:.0f}")
    print(f"Total Yards Per Game: {stats['total_yards_per_game']:.1f}")

    print(f"\nPassing Yards: {stats['passing_yards']:.0f}")
    print(f"Passing Yards Per Game: {stats['passing_yards_per_game']:.1f}")

    print(f"\nRushing Yards: {stats['rushing_yards']:.0f}")
    print(f"Rushing Yards Per Game: {stats['rushing_yards_per_game']:.1f}")

    print("\nTOUCHDOWNS")
    print("----------")
    print(f"Passing TDs: {stats['passing_touchdowns']:.0f}")
    print(f"Rushing TDs: {stats['rushing_touchdowns']:.0f}")
    print(f"Total Offensive TDs: {stats['total_touchdowns']:.0f}")

    print("\nTURNOVERS")
    print("---------")
    print(f"Interceptions Thrown: {stats['interceptions']:.0f}")
    print(f"Fumbles Lost: {stats['fumbles_lost']:.0f}")
    print(f"Total Turnovers: {stats['total_turnovers']:.0f}")

    print("\nEFFICIENCY")
    print("----------")
    print(f"Offensive Plays: {stats['total_plays']:.0f}")
    print(f"Yards Per Play: {stats['yards_per_play']:.2f}")
    print(f"Passing Yards Per Attempt: {stats['passing_yards_per_attempt']:.2f}")
    print(f"Rushing Yards Per Attempt: {stats['rushing_yards_per_attempt']:.2f}")
    print(
        f"Offensive EPA Per Play: "
        f"{stats['offensive_epa_per_play']:.3f}"  
    )

def display_defensive_stats(stats):
    print("\nDEFENSIVE STATISTICS")
    print("--------------------")

    print(f"Total Yards Allowed: {stats['total_yards_allowed']:.0f}")
    print(f"Yards Allowed Per Game: {stats['yards_allowed_per_game']:.1f}")

    print(f"\nPassing Yards Allowed: {stats['passing_yards_allowed']:.0f}")
    print(
        f"Passing Yards Allowed Per Game: "
        f"{stats['passing_yards_allowed_per_game']:.1f}"
    )
    print(f"Rushing Yards Allowed: {stats['rushing_yards_allowed']:.0f}")
    print(
        f"Rushing Yards Allowed Per Game: "
        f"{stats['rushing_yards_allowed_per_game']:.1f}"
    )
    print(f"Yards Allowed Per Play: {stats['yards_allowed_per_play']:.2f}")
    print(
        f"Defensive EPA Per Play: "
        f"{stats['defensive_epa_per_play']:.3f}"
    )

    print("\nDEFENSIVE IMPACT PLAYS")
    print("----------------------")
    print(f"Sacks: {stats['sacks']:.0f}")
    print(f"Interceptions: {stats['interceptions']:.0f}")
    print(f"Fumbles Recovered: {stats['fumbles_recovered']:.0f}")
    print(f"Takeaways: {stats['takeaways']:.0f}")

def display_team_rankings(all_team_stats, team):
    print("\nNFL RANKINGS")
    print("------------")

    scoring_offense = get_team_rank(
        all_team_stats,
        team,
        "points_per_game",
        True
    )

    total_offense = get_team_rank(
        all_team_stats,
        team,
        "total_yards_per_game",
        True
    )

    passing_offense = get_team_rank(
        all_team_stats,
        team,
        "passing_yards_per_game",
        True
    )

    rushing_offense = get_team_rank(
        all_team_stats,
        team,
        "rushing_yards_per_game",
        True
    )

    scoring_defense = get_team_rank(
        all_team_stats,
        team,
        "points_allowed_per_game",
        False
    )

    total_defense = get_team_rank(
        all_team_stats,
        team,
        "yards_allowed_per_game",
        False
    )

    passing_defense = get_team_rank(
        all_team_stats,
        team,
        "passing_yards_allowed_per_game",
        False
    )

    rushing_defense = get_team_rank(
        all_team_stats,
        team,
        "rushing_yards_allowed_per_game",
        False
    )

    turnover_rank = get_team_rank(
        all_team_stats,
        team,
        "turnover_differential",
        True
    )

    team_stats = next(
        stats for stats in all_team_stats
        if stats["team"] == team
    )

    print(f"Scoring Offense: #{scoring_offense}")
    print(f"Total Offense: #{total_offense}")
    print(f"Passing Offense: #{passing_offense}")
    print(f"Rushing Offense: #{rushing_offense}")

    print(f"\nScoring Defense: #{scoring_defense}")
    print(f"Total Defense: #{total_defense}")
    print(f"Passing Defense: #{passing_defense}")
    print(f"Rushing Defense: #{rushing_defense}")

    print(
        f"\nTurnover Differential: "
        f"{team_stats['turnover_differential']:+.0f}"
    )

    print(f"Turnover Differential Rank: #{turnover_rank}")

def display_team_comparison(all_team_stats, team1, team2):
    team1_stats = next(
        stats for stats in all_team_stats
        if stats["team"] == team1
    )

    team2_stats = next(
        stats for stats in all_team_stats
        if stats["team"] == team2
    )

    print("\nTEAM COMPARISON")
    print("===============")
    print(f"{team1} vs {team2}")

    print("\nOFFENSE")
    print("-------")
    print(
        f"Points Per Game: "
        f"{team1} {team1_stats['points_per_game']:.1f} | "
        f"{team2} {team2_stats['points_per_game']:.1f}"
    )

    print(
        f"Total Yards Per Game: "
        f"{team1} {team1_stats['total_yards_per_game']:.1f} | "
        f"{team2} {team2_stats['total_yards_per_game']:.1f}"
    )

    print(
        f"Passing Yards Per Game: "
        f"{team1} {team1_stats['passing_yards_per_game']:.1f} | "
        f"{team2} {team2_stats['passing_yards_per_game']:.1f}"
    )

    print(
        f"Rushing Yards Per Game: "
        f"{team1} {team1_stats['rushing_yards_per_game']:.1f} | "
        f"{team2} {team2_stats['rushing_yards_per_game']:.1f}"
    )

    print("\nDEFENSE")
    print("-------")
    print(
        f"Points Allowed Per Game: "
        f"{team1} {team1_stats['points_allowed_per_game']:.1f} | "
        f"{team2} {team2_stats['points_allowed_per_game']:.1f}"
    )

    print(
        f"Yards Allowed Per Game: "
        f"{team1} {team1_stats['yards_allowed_per_game']:.1f} | "
        f"{team2} {team2_stats['yards_allowed_per_game']:.1f}"
    )

    print(
        f"Passing Yards Allowed Per Game: "
        f"{team1} {team1_stats['passing_yards_allowed_per_game']:.1f} | "
        f"{team2} {team2_stats['passing_yards_allowed_per_game']:.1f}"
    )

    print(
        f"Rushing Yards Allowed Per Game: "
        f"{team1} {team1_stats['rushing_yards_allowed_per_game']:.1f} | "
        f"{team2} {team2_stats['rushing_yards_allowed_per_game']:.1f}"
    )

    print("\nTURNOVERS")
    print("---------")
    print(
        f"Turnover Differential: "
        f"{team1} {team1_stats['turnover_differential']:+.0f} | "
        f"{team2} {team2_stats['turnover_differential']:+.0f}"
    )

def display_matchup_prediction(prediction, team1, team2):
    team1_score = prediction["team1_projected_points"]
    team2_score = prediction["team2_projected_points"]

    print("\nMATCHUP PREDICTION")
    print("------------------")
    print(f"{team1} vs {team2}")

    print("\nProjected Score")
    print("---------------")
    print(f"{team1}: {team1_score:.1f}")
    print(f"{team2}: {team2_score:.1f}")

    if team1_score > team2_score:
        winner = team1
        margin = team1_score - team2_score

    elif team2_score > team1_score:
        winner = team2
        margin = team2_score - team1_score

    else:
        winner = "Tie"
        margin = 0

    print(f"\nPredicted Winner: {winner}")

    if winner != "Tie":
        print(f"Projected Margin: {margin:.1f} points")

# ============================================================
# ML DATASET DISPLAY
# ============================================================

def display_ml_dataset_sample(ml_dataset):

    print("\nML DATASET")
    print("----------")
    print(f"Rows: {len(ml_dataset)}")

    print("\nFIRST ML DATASET ROW")
    print("--------------------")

    first_row = ml_dataset[0]

    print(f"Season: {first_row['season']}")
    print(f"Week: {first_row['week']}")
    print(
        f"Matchup: "
        f"{first_row['away_team']} @ "
        f"{first_row['home_team']}"
    )

    print("\nOFFENSE")
    print("-------")
    print(
        f"Points Per Game: "
        f"{first_row['away_team']} "
        f"{first_row['away_points_per_game']:.1f} | "
        f"{first_row['home_team']} "
        f"{first_row['home_points_per_game']:.1f}"
    )

    print(
        f"Yards Per Game: "
        f"{first_row['away_team']} "
        f"{first_row['away_yards_per_game']:.1f} | "
        f"{first_row['home_team']} "
        f"{first_row['home_yards_per_game']:.1f}"
    )

    print("\nDEFENSE")
    print("-------")
    print(
        f"Points Allowed Per Game: "
        f"{first_row['away_team']} "
        f"{first_row['away_points_allowed_per_game']:.1f} | "
        f"{first_row['home_team']} "
        f"{first_row['home_points_allowed_per_game']:.1f}"
    )

    print(
        f"Yards Allowed Per Game: "
        f"{first_row['away_team']} "
        f"{first_row['away_yards_allowed_per_game']:.1f} | "
        f"{first_row['home_team']} "
        f"{first_row['home_yards_allowed_per_game']:.1f}"
    )

    print("\nTURNOVER DIFFERENTIAL PER GAME")
    print("------------------------------")

    print(
        f"{first_row['away_team']}: "
        f"{first_row['away_turnover_diff_per_game']:+.1f}"
    )

    print(
        f"{first_row['home_team']}: "
        f"{first_row['home_turnover_diff_per_game']:+.1f}"
    )

    print("\nACTUAL RESULT")
    print("-------------")

    if first_row["home_win"] == 1:
        print(f"Winner: {first_row['home_team']}")
    else:
        print(f"Winner: {first_row['away_team']}")

# ============================================================
# ML PREDICTION DISPLAY
# ============================================================

def display_ml_predictions(
    ml_dataset,
    ml_predictions,
    ml_probabilities,
    num_games=5
):
    print("\nSAMPLE ML PREDICTIONS")
    print("---------------------")

    for i in range(num_games):

        game = ml_dataset[i]

        home_team = game["home_team"]
        away_team = game["away_team"]

        home_probability = ml_probabilities[i] * 100
        away_probability = 100 - home_probability

        if ml_predictions[i] == 1:
            predicted_winner = home_team
        else:
            predicted_winner = away_team

        if game["home_win"] == 1:
            actual_winner = home_team
        else:
            actual_winner = away_team

        if predicted_winner == actual_winner:
            result = "CORRECT"
        else:
            result = "WRONG"

        print(f"\n{away_team} @ {home_team}")
        print(f"{away_team}: {away_probability:.1f}%")
        print(f"{home_team}: {home_probability:.1f}%")
        print(f"Predicted Winner: {predicted_winner}")
        print(f"Actual Winner: {actual_winner}")
        print(f"Result: {result}")