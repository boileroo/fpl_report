import os
from functions.file_operations import load_or_create_all_time_stats, save_to_json

class AllTimeStatsManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.stats = load_or_create_all_time_stats(filepath)
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

    def save_stats(self):
        save_to_json(self.stats, self.filepath)
        print(f"All-time stats saved to {self.filepath}")