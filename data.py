# ============================================================
# DATA LOADING
# ============================================================

import nflreadpy as nfl


def load_nfl_data(season):

    games = nfl.load_schedules(season)

    print("\nLoading play-by-play data...")
    pbp = nfl.load_pbp(season)

    return games, pbp