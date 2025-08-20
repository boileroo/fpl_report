import copy
import statistics
import json
from pathlib import Path
from functions.utils import ensure_output_directory_exists, save_to_json

class AllTimeStatsManager:
    def __init__(self, league_name, gameweek):
        self.league_name = league_name
        self.gameweek = gameweek
        self.previous_gameweek = gameweek - 1
        self.filepath = self._get_gameweek_filepath(league_name, gameweek)
        self.previous_gw_filepath = self._get_gameweek_filepath(league_name, self.previous_gameweek)
        
        self._ensure_output_directory()
        self._initialize_stats()

    def _get_gameweek_filepath(self, league_name, gameweek):
        filename = f"all_time_stats_gw_{gameweek}.json"
        return Path("outputs") / league_name / f"gameweek_{gameweek}" / filename

    def _ensure_output_directory(self):
        ensure_output_directory_exists(self.filepath)

    def _load_or_create_all_time_stats(self, filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_stats_structure()

    def _get_default_stats_structure(self):
        return {
            "records": {
                "highest_gw_score": {"team": None, "gameweek": None, "value": 0},
                "lowest_gw_score": {"team": None, "gameweek": None, "value": float('inf')},
                "most_points_on_bench": {"team": None, "gameweek": None, "value": 0},
                "highest_team_value": {"team": None, "gameweek": None, "value": 0},
                "biggest_bank_balance": {"team": None, "gameweek": None, "value": 0},
                "most_captain_points": {"team": None, "gameweek": None, "value": 0},
                "worst_captain_points": {"team": None, "gameweek": None, "value": float('inf')},
                "most_transfers": {"team": None, "gameweek": None, "value": 0},
                "highest_overall_gameweek_rank": {"team": None, "gameweek": None, "value": float('inf')},
                "lowest_overall_gameweek_rank": {"team": None, "gameweek": None, "value": 0},
                "highest_league_rank": {"team": None, "gameweek": None, "value": float('inf')},
                "lowest_league_rank": {"team": None, "gameweek": None, "value": 0},
                "biggest_league_rank_drop": {"team": None, "gameweek": None, "value": float('inf')},
                "biggest_league_rank_climb": {"team": None, "gameweek": None, "value": 0},
                "highest_defensive_haul": {"team": None, "gameweek": None, "value": 0},
                "highest_attacking_haul": {"team": None, "gameweek": None, "value": 0},
                "narrowest_gw_score_variance": {"team": None, "gameweek": None, "value": float('inf')},
                "widest_gw_score_variance": {"team": None, "gameweek": None, "value": 0},
                "best_autosub_cameo": {"team": None, "gameweek": None, "value": 0, "player": None},
                "best_chip_play": {"team": None, "gameweek": None, "value": 0, "chip": None, "player": None},
                "worst_chip_play": {"team": None, "gameweek": None, "value": float('inf'), "chip": None, "player": None}
            },
            "cumulative": {
                "captaincy_points": {},
                "bench_points": {},
                "bank_balance": {},
                "defensive_points": {},
                "attacking_points": {},
                "autosub_points": {}
            },
            "counts": {
                "captain_choices": {},
                "formations": {},
                "chip_usage": {},
                "gameweek_participation": {}
            },
            "manager_records": {
                "highest_league_rank": {},
                "lowest_league_rank": {}
            },
            "formations": {
                "highest_score_by_formation": {}
            },
            "gw_scores": {},
            "differential_king_per_gameweek": {}
        }

    def _initialize_stats(self):
        # Load current gameweek stats (this will either load existing or create default structure)
        self.all_time_stats = self._load_or_create_all_time_stats(str(self.filepath))
        
        # Check if current stats have the old flat structure and convert if needed
        if self.all_time_stats and isinstance(self.all_time_stats, dict):
            # Check if it has the old flat structure (look for keys that should be in records category)
            old_record_keys = [
                "highest_gw_score", "lowest_gw_score", "most_points_on_bench",
                "highest_team_value", "biggest_bank_balance", "most_captain_points",
                "worst_captain_points", "most_transfers", "highest_overall_gameweek_rank",
                "lowest_overall_gameweek_rank", "highest_league_rank", "lowest_league_rank",
                "biggest_league_rank_drop", "biggest_league_rank_climb", "highest_defensive_haul",
                "highest_attacking_haul", "narrowest_gw_score_variance", "widest_gw_score_variance",
                "best_autosub_cameo", "best_chip_play", "worst_chip_play"
            ]
            
            # If we find old record keys at the top level, it's the old structure
            if any(key in self.all_time_stats for key in old_record_keys):
                # Convert old flat structure to new hierarchical structure
                new_stats = self._get_default_stats_structure()
                
                # Copy record data
                for key in old_record_keys:
                    if key in self.all_time_stats:
                        new_stats["records"][key] = self.all_time_stats[key]
                
                # Copy cumulative data using the same mapping as before
                key_mapping = {
                    "total_captaincy_points_per_manager": ("cumulative", "captaincy_points"),
                    "most_popular_captain_choices": ("counts", "captain_choices"),
                    "total_bench_points_wasted_per_manager": ("cumulative", "bench_points"),
                    "total_bank_balance_per_manager": ("cumulative", "bank_balance"),
                    "gameweek_count_per_manager": ("counts", "gameweek_participation"),
                    "most_common_formations": ("counts", "formations"),
                    "chip_usage_tally": ("counts", "chip_usage"),
                    "total_defensive_points_per_manager": ("cumulative", "defensive_points"),
                    "total_attacking_points_per_manager": ("cumulative", "attacking_points"),
                    "gw_scores_per_manager": ("gw_scores", "gw_scores"),
                    "total_autosub_points_per_manager": ("cumulative", "autosub_points"),
                    "highest_league_rank_per_manager": ("manager_records", "highest_league_rank"),
                    "lowest_league_rank_per_manager": ("manager_records", "lowest_league_rank"),
                    "differential_king_per_gameweek": ("differential_king_per_gameweek", "differential_king_per_gameweek"),  # Direct mapping
                    "highest_overall_rank": ("records", "highest_overall_rank"),
                    "lowest_overall_rank": ("records", "lowest_overall_rank")
                }
                
                # Copy data from old structure to new structure
                for old_key, (new_category, new_key) in key_mapping.items():
                    if old_key in self.all_time_stats:
                        # Special handling for gw_scores and differential_king_per_gameweek
                        if new_category in ["gw_scores", "differential_king_per_gameweek"]:
                            new_stats[new_category] = self.all_time_stats[old_key]
                        else:
                            # For other categories, we need to map the data appropriately
                            new_stats[new_category][new_key] = self.all_time_stats[old_key]
                
                # Replace the current stats with the converted structure
                self.all_time_stats = new_stats
        
        # Load previous gameweek stats if available
        previous_gameweek_stats = {}
        if self.previous_gameweek > 0:
            previous_gameweek_stats = self._load_or_create_all_time_stats(str(self.previous_gw_filepath))
        
        # If we have previous gameweek stats, merge them with current stats
        if previous_gameweek_stats and isinstance(previous_gameweek_stats, dict):
            # Check if previous stats have the new hierarchical structure
            if "cumulative" in previous_gameweek_stats:
                # New structure - copy categories directly
                for category in ["cumulative", "counts"]:
                    if category in previous_gameweek_stats:
                        self.all_time_stats[category] = copy.deepcopy(previous_gameweek_stats[category])
            else:
                # Old flat structure - need to migrate
                # Initialize the new structure categories if they don't exist
                if "cumulative" not in self.all_time_stats:
                    self.all_time_stats["cumulative"] = {
                        "captaincy_points": {},
                        "bench_points": {},
                        "bank_balance": {},
                        "defensive_points": {},
                        "attacking_points": {},
                        "autosub_points": {}
                    }
                    
                if "counts" not in self.all_time_stats:
                    self.all_time_stats["counts"] = {
                        "captain_choices": {},
                        "formations": {},
                        "chip_usage": {},
                        "gameweek_participation": {}
                    }
                
                # Map old keys to new structure
                key_mapping = {
                    "total_captaincy_points_per_manager": ("cumulative", "captaincy_points"),
                    "most_popular_captain_choices": ("counts", "captain_choices"),
                    "total_bench_points_wasted_per_manager": ("cumulative", "bench_points"),
                    "total_bank_balance_per_manager": ("cumulative", "bank_balance"),
                    "gameweek_count_per_manager": ("counts", "gameweek_participation"),
                    "most_common_formations": ("counts", "formations"),
                    "chip_usage_tally": ("counts", "chip_usage"),
                    "total_defensive_points_per_manager": ("cumulative", "defensive_points"),
                    "total_attacking_points_per_manager": ("cumulative", "attacking_points"),
                    "total_autosub_points_per_manager": ("cumulative", "autosub_points")
                }
                
                # Copy data from old structure to new structure
                for old_key, (new_category, new_key) in key_mapping.items():
                    if old_key in previous_gameweek_stats:
                        self.all_time_stats[new_category][new_key] = copy.deepcopy(previous_gameweek_stats[old_key])

    def _update_stat_record(self, stat_category, stat_key, team_name, gameweek, value, is_highest=True, **kwargs):
        if stat_category == "manager_records":
            manager_stat = self.all_time_stats[stat_category].get(stat_key, {})
            current_manager_record = manager_stat.get(team_name, {"value": None})
            current_value = current_manager_record["value"]
            updated = False

            if current_value is None:
                updated = True
            elif is_highest:
                if value > current_value:
                    updated = True
            else: 
                if value < current_value:
                    updated = True

            if updated:
                manager_stat[team_name] = {
                    "gameweek": gameweek,
                    "value": value
                }
                self.all_time_stats[stat_category][stat_key] = manager_stat
        else:
            current_stat = self.all_time_stats[stat_category].get(stat_key, {"value": None})
            current_value = current_stat.get("value", None)  # Use .get() to avoid KeyError
            updated = False

            if current_value is None:
                updated = True
            elif is_highest:
                if value > current_value:
                    updated = True
            else:
                if value < current_value:
                    updated = True

            if updated:
                self.all_time_stats[stat_category][stat_key] = {
                    "team": team_name,
                    "gameweek": gameweek,
                    "value": value
                }
                
                for key, val in kwargs.items():
                    if val is not None:
                        self.all_time_stats[stat_category][stat_key][key] = val

    def _increment_stat_count(self, category, key, increment=1):
        self.all_time_stats["counts"][category][key] = self.all_time_stats["counts"][category].get(key, 0) + increment

    def _add_cumulative_stat(self, category, team_name, value):
        self.all_time_stats["cumulative"][category][team_name] = self.all_time_stats["cumulative"][category].get(team_name, 0) + value

    # Backward compatibility methods - these maintain the same interface as the original
    
    def update_highest_gw_score(self, team_name, gameweek, value):
        self._update_stat_record("records", "highest_gw_score", team_name, gameweek, value, is_highest=True)

    def update_lowest_gw_score(self, team_name, gameweek, value):
        self._update_stat_record("records", "lowest_gw_score", team_name, gameweek, value, is_highest=False)

    def update_most_points_on_bench(self, team_name, gameweek, value):
        self._update_stat_record("records", "most_points_on_bench", team_name, gameweek, value, is_highest=True)

    def update_highest_team_value(self, team_name, gameweek, value):
        self._update_stat_record("records", "highest_team_value", team_name, gameweek, value, is_highest=True)

    def update_biggest_bank_balance(self, team_name, gameweek, value):
        self._update_stat_record("records", "biggest_bank_balance", team_name, gameweek, value, is_highest=True)

    def update_most_captain_points(self, team_name, gameweek, value, player_name):
        self._update_stat_record("records", "most_captain_points", team_name, gameweek, value, is_highest=True, player=player_name)

    def update_worst_captain_points(self, team_name, gameweek, value, player_name):
        self._update_stat_record("records", "worst_captain_points", team_name, gameweek, value, is_highest=False, player=player_name)

    def update_most_transfers(self, team_name, gameweek, value):
        self._update_stat_record("records", "most_transfers", team_name, gameweek, value, is_highest=True)

    def update_best_chip_play(self, team_name, gameweek, value, chip_name, player_name=None):
        self._update_stat_record("records", "best_chip_play", team_name, gameweek, value, is_highest=True, chip=chip_name, player=player_name)

    def update_worst_chip_play(self, team_name, gameweek, value, chip_name, player_name=None):
        self._update_stat_record("records", "worst_chip_play", team_name, gameweek, value, is_highest=False, chip=chip_name, player=player_name)

    def update_highest_defensive_haul(self, team_name, gameweek, value):
        self._update_stat_record("records", "highest_defensive_haul", team_name, gameweek, value, is_highest=True)

    def update_highest_attacking_haul(self, team_name, gameweek, value):
        self._update_stat_record("records", "highest_attacking_haul", team_name, gameweek, value, is_highest=True)

    def update_chip_usage_tally(self, team_name, chip_name):
        self.all_time_stats["counts"]["chip_usage"].setdefault(team_name, {}).setdefault(chip_name, 0)
        self.all_time_stats["counts"]["chip_usage"][team_name][chip_name] += 1

    def update_highest_overall_gameweek_rank(self, team_name, gameweek, value):
        self._update_stat_record("records", "highest_overall_gameweek_rank", team_name, gameweek, value, is_highest=False)

    def update_lowest_overall_gameweek_rank(self, team_name, gameweek, value):
        self._update_stat_record("records", "lowest_overall_gameweek_rank", team_name, gameweek, value, is_highest=True)

    def update_highest_overall_rank(self, team_name, gameweek, value):
        self._update_stat_record("records", "highest_overall_rank", team_name, gameweek, value, is_highest=False)

    def update_lowest_overall_rank(self, team_name, gameweek, value):
        self._update_stat_record("records", "lowest_overall_rank", team_name, gameweek, value, is_highest=True)

    def update_biggest_league_rank_drop(self, team_name, gameweek, value):
        self._update_stat_record("records", "biggest_league_rank_drop", team_name, gameweek, value, is_highest=False)

    def update_biggest_league_rank_climb(self, team_name, gameweek, value):
        self._update_stat_record("records", "biggest_league_rank_climb", team_name, gameweek, value, is_highest=True)

    def update_highest_league_rank_per_manager(self, team_name, gameweek, value):
        self._update_stat_record("manager_records", "highest_league_rank", team_name, gameweek, value, is_highest=False)

    def update_lowest_league_rank_per_manager(self, team_name, gameweek, value):
        self._update_stat_record("manager_records", "lowest_league_rank", team_name, gameweek, value, is_highest=True)

    def update_total_captaincy_points_per_manager(self, team_name, captain_points):
        self._add_cumulative_stat("captaincy_points", team_name, captain_points)

    def update_most_popular_captain_choices(self, player_name):
        self._increment_stat_count("captain_choices", player_name)

    def update_total_bench_points_wasted_per_manager(self, team_name, bench_points):
        self._add_cumulative_stat("bench_points", team_name, bench_points)

    def update_best_autosub_cameo(self, team_name, gameweek, player_name, points):
        self._update_stat_record("records", "best_autosub_cameo", team_name, gameweek, points, is_highest=True, player=player_name)

    def update_total_defensive_points_per_manager(self, team_name, defensive_points):
        self._add_cumulative_stat("defensive_points", team_name, defensive_points)

    def update_total_attacking_points_per_manager(self, team_name, attacking_points):
        self._add_cumulative_stat("attacking_points", team_name, attacking_points)

    def update_total_autosub_points_per_manager(self, team_name, autosub_points):
        self._add_cumulative_stat("autosub_points", team_name, autosub_points)

    def update_all_stats_for_manager(self, gw_data, team_name, gameweek_int, entry=None):
        self._update_basic_records(gw_data, team_name, gameweek_int)
        self._update_league_rank_stats(gw_data, team_name, gameweek_int)
        self._update_cumulative_stats(gw_data, team_name, gameweek_int)
        self._update_formation_stats(gw_data, team_name, gameweek_int)
        self._update_chip_stats(gw_data, team_name, gameweek_int)
        self._update_performance_stats(gw_data, team_name, gameweek_int)
        
        return self.all_time_stats

    def _update_basic_records(self, gw_data, team_name, gameweek_int):
        self.update_highest_gw_score(team_name, gameweek_int, gw_data['Points'])
        self.update_lowest_gw_score(team_name, gameweek_int, gw_data['Points'])
        self.update_most_points_on_bench(team_name, gameweek_int, gw_data['Points on Bench'])
        self.update_highest_team_value(team_name, gameweek_int, gw_data['Team Value'])
        self.update_biggest_bank_balance(team_name, gameweek_int, gw_data['Bank Money'])
        self.update_most_captain_points(team_name, gameweek_int, gw_data['Captain Points'], gw_data['Captain'])
        self.update_worst_captain_points(team_name, gameweek_int, gw_data['Captain Points'], gw_data['Captain'])
        self.update_most_transfers(team_name, gameweek_int, gw_data['Transfers'])
        self.update_highest_overall_rank(team_name, gameweek_int, gw_data['Overall Rank'])
        self.update_lowest_overall_rank(team_name, gameweek_int, gw_data['Overall Rank'])
        self.update_highest_overall_gameweek_rank(team_name, gameweek_int, gw_data['Overall Gameweek Rank'])
        self.update_lowest_overall_gameweek_rank(team_name, gameweek_int, gw_data['Overall Gameweek Rank'])

    def _update_league_rank_stats(self, gw_data, team_name, gameweek_int):
        if self.gameweek == 1:
            league_rank_movement_for_stats = 0
        else:
            league_rank_movement_for_stats = gw_data.get('League Rank Movement', 0)
            
        if league_rank_movement_for_stats < 0:
            self.update_biggest_league_rank_drop(team_name, gameweek_int, league_rank_movement_for_stats)
        elif league_rank_movement_for_stats > 0:
            self.update_biggest_league_rank_climb(team_name, gameweek_int, league_rank_movement_for_stats)

        self.update_highest_league_rank_per_manager(team_name, gameweek_int, gw_data['League Rank'])
        self.update_lowest_league_rank_per_manager(team_name, gameweek_int, gw_data['League Rank'])

    def _update_cumulative_stats(self, gw_data, team_name, gameweek_int):
        self.update_total_captaincy_points_per_manager(team_name, gw_data['Captain Points'])
        self.update_most_popular_captain_choices(gw_data['Captain'])
        self.update_total_bench_points_wasted_per_manager(team_name, gw_data['Points on Bench'])
        self.update_total_autosub_points_per_manager(team_name, gw_data.get('autosub_points', 0))
        
        self._add_cumulative_stat("bank_balance", team_name, gw_data['Bank Money'])
        self._increment_stat_count("gameweek_participation", team_name)
        
        self.update_total_defensive_points_per_manager(team_name, gw_data['Defensive Points'])
        self.update_total_attacking_points_per_manager(team_name, gw_data['Attacking Points'])

    def _update_formation_stats(self, gw_data, team_name, gameweek_int):
        formation = gw_data.get('Formation')
        if formation:
            self._increment_stat_count("formations", formation)
            self.update_highest_score_by_formation(formation, team_name, gameweek_int, gw_data['Points'])

    def _update_chip_stats(self, gw_data, team_name, gameweek_int):
        chip_used = gw_data.get('Chip Used', "No Chip Used")
        if chip_used != "No Chip Used" and chip_used != "No Chip":
            self.update_chip_usage_tally(team_name, chip_used)
            if chip_used in ["BB", "TC", "FH", "WC"]:
                self.update_best_chip_play(team_name, gameweek_int, gw_data['Points'], chip_used)
                self.update_worst_chip_play(team_name, gameweek_int, gw_data['Points'], chip_used)

    def _update_performance_stats(self, gw_data, team_name, gameweek_int):
        self.update_highest_defensive_haul(team_name, gameweek_int, gw_data['Defensive Points'])
        self.update_highest_attacking_haul(team_name, gameweek_int, gw_data['Attacking Points'])
        
        manager_gw_scores = self.all_time_stats["gw_scores"].get(team_name, [])
        if len(manager_gw_scores) >= 2:
            gw_variance = statistics.variance(manager_gw_scores)
            self.update_narrowest_gw_score_variance(team_name, gameweek_int, gw_variance)
            self.update_widest_gw_score_variance(team_name, gameweek_int, gw_variance)

        # Replace the gw_scores list with just the current gameweek's score
        # instead of appending to prevent duplicates across runs
        self.all_time_stats["gw_scores"][team_name] = [gw_data['Points']]

    def process_differential_king(self, differential_king_data):
        if differential_king_data:
            self.update_differential_king_per_gameweek(
                gameweek=self.gameweek,
                player_name=differential_king_data['player_name'],
                points=differential_king_data['points'],
                team_name=differential_king_data['owner']
            )

    def update_differential_king_per_gameweek(self, gameweek, player_name, points, team_name):
        current_differential_king = self.all_time_stats["differential_king_per_gameweek"].get(str(gameweek))
        
        updated = False
        if current_differential_king is None:
            updated = True
        elif points > current_differential_king["points"]:
            updated = True
            
        if updated:
            self.all_time_stats["differential_king_per_gameweek"][str(gameweek)] = {
                "player": player_name,
                "points": points,
                "team": team_name
            }

    def update_narrowest_gw_score_variance(self, team_name, gameweek, variance):
        self._update_stat_record("records", "narrowest_gw_score_variance", team_name, gameweek, variance, is_highest=False)
        
    def update_widest_gw_score_variance(self, team_name, gameweek, variance):
        self._update_stat_record("records", "widest_gw_score_variance", team_name, gameweek, variance, is_highest=True)

    def update_most_common_formations(self, formation):
        self._increment_stat_count("formations", formation)

    def update_highest_score_by_formation(self, formation, team_name, gameweek, score):
        current_highest = self.all_time_stats["formations"]["highest_score_by_formation"].get(formation, {"value": None})
        if current_highest["value"] is None or score > current_highest["value"]:
            self.all_time_stats["formations"]["highest_score_by_formation"][formation] = {
                "team": team_name,
                "gameweek": gameweek,
                "value": score
            }
    
    @property
    def stats(self):
        """Backward compatibility property to access all_time_stats as stats."""
        return self.all_time_stats
    
    def save_stats(self):
        save_to_json(self.all_time_stats, str(self.filepath))