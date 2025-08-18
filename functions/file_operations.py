import json

def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def load_or_create_all_time_stats(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Initialize with default values
        default_stats = {
            "highest_gw_score": {"team": None, "gameweek": None, "value": 0},
            "lowest_gw_score": {"team": None, "gameweek": None, "value": float('inf')},
            "most_points_on_bench": {"team": None, "gameweek": None, "value": 0},
            "highest_team_value": {"team": None, "gameweek": None, "value": 0},
            "biggest_bank_balance": {"team": None, "gameweek": None, "value": 0}, # Added missing key
            "most_captain_points": {"team": None, "gameweek": None, "value": 0},
            "worst_captain_points": {"team": None, "gameweek": None, "value": float('inf')},
            "most_transfers": {"team": None, "gameweek": None, "value": 0},
            "highest_overall_gameweek_rank": {"team": None, "gameweek": None, "value": float('inf')},
            "lowest_overall_gameweek_rank": {"team": None, "gameweek": None, "value": 0},
            "highest_overall_rank": {"team": None, "gameweek": None, "value": float('inf')},
            "lowest_overall_rank": {"team": None, "gameweek": None, "value": 0},
            "biggest_league_rank_drop": {"team": None, "gameweek": None, "value": float('inf')}, # Changed default to inf for lowest
            "biggest_league_rank_climb": {"team": None, "gameweek": None, "value": 0}, # Rank climb is typically negative, so '0' is not correct lowest value. Should be -float('inf').
            "highest_defensive_haul": {"team": None, "gameweek": None, "value": 0}, # Added missing key
            "highest_attacking_haul": {"team": None, "gameweek": None, "value": 0}, # Added missing key
            "narrowest_gw_score_variance": {"team": None, "gameweek": None, "value": float('inf')}, # Added missing key
            "widest_gw_score_variance": {"team": None, "gameweek": None, "value": 0}, # Added missing key
            "total_captaincy_points_per_manager": {},
            "most_popular_captain_choices": {},
            "total_bench_points_wasted_per_manager": {},
            "total_bank_balance_per_manager": {}, # Added missing key
            "gameweek_count_per_manager": {}, # Added missing key
            "most_common_formations": {}, # Added missing key
            "highest_score_by_formation": {}, # Added missing key
            "gw_scores_per_manager": {}, # Added missing key
            "best_autosub_cameo": {"team": None, "gameweek": None, "value": 0, "player": None},
            "best_chip_play": {"team": None, "gameweek": None, "value": 0, "chip": None, "player": None},
            "worst_chip_play": {"team": None, "gameweek": None, "value": float('inf'), "chip": None, "player": None},
            "chip_usage_tally": {},
            "unusual_formations_spotted": [] # Added missing key
        }
        return default_stats