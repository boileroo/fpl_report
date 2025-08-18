import os
import copy
from functions.file_operations import load_or_create_all_time_stats, save_to_json

class AllTimeStatsManager:
    def __init__(self, base_filepath, current_gameweek):
        self.base_filepath = base_filepath
        self.current_gameweek = current_gameweek
        
        # Construct filepath for the current gameweek
        filename, ext = os.path.splitext(os.path.basename(base_filepath))
        current_gw_filename = f"{filename}_gw_{current_gameweek}{ext}"
        self.filepath = os.path.join(os.path.dirname(base_filepath), current_gw_filename)

        # Load previous gameweek's stats
        previous_gameweek_stats = {}
        previous_gameweek = current_gameweek - 1
        if previous_gameweek > 0:
            previous_gw_filename = f"{filename}_gw_{previous_gameweek}{ext}"
            previous_gw_filepath = os.path.join(os.path.dirname(base_filepath), previous_gw_filename)
            previous_gameweek_stats = load_or_create_all_time_stats(previous_gw_filepath)
        
        # Initialize current stats with defaults
        self.stats = load_or_create_all_time_stats(self.filepath) # This will create default if file doesn't exist

        # Copy cumulative stats from previous gameweek
        # These are the stats that should carry over and accumulate
        cumulative_keys = [
            "total_captaincy_points_per_manager",
            "most_popular_captain_choices",
            "total_bench_points_wasted_per_manager",
            "total_bank_balance_per_manager",
            "gameweek_count_per_manager"
        ]
        
        for key in cumulative_keys:
            if key in previous_gameweek_stats:
                self.stats[key] = copy.deepcopy(previous_gameweek_stats[key])
            else:
                self.stats[key] = {} # Ensure it's initialized if not present in previous

        self._ensure_output_directory_exists()

    def _ensure_output_directory_exists(self):
        output_dir = os.path.dirname(self.filepath)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def _update_stat(self, stat_key, team_name, gameweek, value, is_highest=True, player_name=None):
        current_stat = self.stats.get(stat_key, {"value": None})
        current_value = current_stat["value"]
        updated = False

        if current_value is None: # Initialize if not set
            updated = True
        elif is_highest:
            if value > current_value:
                updated = True
        else: # is_lowest
            if value < current_value:
                updated = True

        if updated:
            self.stats[stat_key] = {
                "team": team_name,
                "gameweek": gameweek,
                "value": value
            }
            if player_name:
                self.stats[stat_key]["player"] = player_name
            print(f"Updated all-time {stat_key}: {value} by ({team_name}) in GW {gameweek}{f' (Player: {player_name})' if player_name else ''}")

    def update_highest_gw_score(self, team_name, gameweek, value):
        self._update_stat("highest_gw_score", team_name, gameweek, value, is_highest=True)

    def update_lowest_gw_score(self, team_name, gameweek, value):
        self._update_stat("lowest_gw_score", team_name, gameweek, value, is_highest=False)

    def update_most_points_on_bench(self, team_name, gameweek, value):
        self._update_stat("most_points_on_bench", team_name, gameweek, value, is_highest=True)

    def update_highest_team_value(self, team_name, gameweek, value):
        self._update_stat("highest_team_value", team_name, gameweek, value, is_highest=True)

    def update_biggest_bank_balance(self, team_name, gameweek, value):
        self._update_stat("biggest_bank_balance", team_name, gameweek, value, is_highest=True)

    def update_most_captain_points(self, team_name, gameweek, value, player_name):
        self._update_stat("most_captain_points", team_name, gameweek, value, is_highest=True, player_name=player_name)

    def update_worst_captain_points(self, team_name, gameweek, value, player_name):
        self._update_stat("worst_captain_points", team_name, gameweek, value, is_highest=False, player_name=player_name)

    def update_most_transfers(self, team_name, gameweek, value):
        self._update_stat("most_transfers", team_name, gameweek, value, is_highest=True)

    def update_highest_gw_rank(self, team_name, gameweek, value):
        self._update_stat("highest_gw_rank", team_name, gameweek, value, is_highest=False) # Lower rank is better

    def update_lowest_gw_rank(self, team_name, gameweek, value):
        self._update_stat("lowest_gw_rank", team_name, gameweek, value, is_highest=True) # Higher rank is worse

    def update_highest_overall_rank(self, team_name, gameweek, value):
        self._update_stat("highest_overall_rank", team_name, gameweek, value, is_highest=False) # Lower rank is better

    def update_lowest_overall_rank(self, team_name, gameweek, value):
        self._update_stat("lowest_overall_rank", team_name, gameweek, value, is_highest=True) # Higher rank is worse

    def update_biggest_rank_drop(self, team_name, gameweek, value):
        self._update_stat("biggest_rank_drop", team_name, gameweek, value, is_highest=True)

    def update_biggest_rank_climb(self, team_name, gameweek, value):
        self._update_stat("biggest_rank_climb", team_name, gameweek, value, is_highest=True)

    def update_total_captaincy_points_per_manager(self, team_name, captain_points):
        if "total_captaincy_points_per_manager" not in self.stats:
            self.stats["total_captaincy_points_per_manager"] = {}
        self.stats["total_captaincy_points_per_manager"][team_name] = self.stats["total_captaincy_points_per_manager"].get(team_name, 0) + captain_points
        print(f"Updated total captaincy points for {team_name}: {self.stats['total_captaincy_points_per_manager'][team_name]}")

    def update_most_popular_captain_choices(self, player_name):
        if "most_popular_captain_choices" not in self.stats:
            self.stats["most_popular_captain_choices"] = {}
        self.stats["most_popular_captain_choices"][player_name] = self.stats["most_popular_captain_choices"].get(player_name, 0) + 1
        print(f"Updated captain count for {player_name}: {self.stats['most_popular_captain_choices'][player_name]}")

    def update_total_bench_points_wasted_per_manager(self, team_name, bench_points):
        if "total_bench_points_wasted_per_manager" not in self.stats:
            self.stats["total_bench_points_wasted_per_manager"] = {}
        self.stats["total_bench_points_wasted_per_manager"][team_name] = self.stats["total_bench_points_wasted_per_manager"].get(team_name, 0) + bench_points
        print(f"Updated total bench points wasted for {team_name}: {self.stats['total_bench_points_wasted_per_manager'][team_name]}")

    def update_best_autosub_cameo(self, team_name, gameweek, player_name, points):
        self._update_stat("best_autosub_cameo", team_name, gameweek, points, is_highest=True, player_name=player_name)

    def update_all_stats_for_manager(self, gw_data, team_name, gameweek_int, manager_data):
        # Update individual stats using the manager's methods
        self.update_highest_gw_score(team_name, gameweek_int, gw_data['Points'])
        self.update_lowest_gw_score(team_name, gameweek_int, gw_data['Points'])
        self.update_most_points_on_bench(team_name, gameweek_int, gw_data['Points on Bench'])
        self.update_highest_team_value(team_name, gameweek_int, gw_data['Team Value'])
        self.update_biggest_bank_balance(team_name, gameweek_int, gw_data['Bank Money'])
        self.update_most_captain_points(team_name, gameweek_int, gw_data['Captain Points'], gw_data['Captain'])
        self.update_worst_captain_points(team_name, gameweek_int, gw_data['Captain Points'], gw_data['Captain'])
        self.update_most_transfers(team_name, gameweek_int, gw_data['Transfers'])
        self.update_highest_gw_rank(team_name, gameweek_int, gw_data['Rank']) # Lower rank is better
        self.update_lowest_gw_rank(team_name, gameweek_int, gw_data['Rank']) # Higher rank is worse
        # Only update overall ranks if a valid rank is present (i.e., not 0)
        if manager_data.get('rank', 0) > 0:
            self.update_highest_overall_rank(team_name, gameweek_int, manager_data['rank'])
            self.update_lowest_overall_rank(team_name, gameweek_int, manager_data['rank'])
        self.update_biggest_rank_drop(team_name, gameweek_int, gw_data['Rank Movement']) # Assuming rank_change is drop if positive
        self.update_biggest_rank_climb(team_name, gameweek_int, gw_data['Rank Movement']) # Assuming rank_change is climb if negative

        # Update cumulative stats
        self.update_total_captaincy_points_per_manager(team_name, gw_data['Captain Points'])
        self.update_most_popular_captain_choices(gw_data['Captain'])
        self.update_total_bench_points_wasted_per_manager(team_name, gw_data['Points on Bench'])

        # Update total bank balance per manager
        self.stats["total_bank_balance_per_manager"][team_name] = self.stats["total_bank_balance_per_manager"].get(team_name, 0) + gw_data['Bank Money']

        # Update gameweek count per manager
        self.stats["gameweek_count_per_manager"][team_name] = self.stats["gameweek_count_per_manager"].get(team_name, 0) + 1

        return self.stats

    def save_stats(self):
        save_to_json(self.stats, self.filepath)
        print(f"All-time stats saved to {self.filepath}")