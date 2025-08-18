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

        # Get the league name from the base filepath
        league_name = os.path.basename(os.path.dirname(base_filepath))

        # Create gameweek-specific directory path
        gameweek_dir = os.path.join("outputs", league_name, f"gameweek_{current_gameweek}")
        self.filepath = os.path.join(gameweek_dir, current_gw_filename)

        # Load previous gameweek's stats
        previous_gameweek_stats = {}
        previous_gameweek = current_gameweek - 1
        if previous_gameweek > 0:
            previous_gw_filename = f"{filename}_gw_{previous_gameweek}{ext}"
            previous_gw_dir = os.path.join("outputs", league_name, f"gameweek_{previous_gameweek}")
            previous_gw_filepath = os.path.join(previous_gw_dir, previous_gw_filename)
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
            "gameweek_count_per_manager",
            "most_common_formations",
            "highest_score_by_formation",
            "chip_usage_tally"
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

    def _update_stat(self, stat_key, team_name, gameweek, value, is_highest=True, player_name=None, chip_name=None):
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
            if chip_name:
                self.stats[stat_key]["chip"] = chip_name
            print(f"Updated all-time {stat_key}: {value} by ({team_name}) in GW {gameweek}{f' (Player: {player_name})' if player_name else ''}{f' (Chip: {chip_name})' if chip_name else ''}")

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

    def update_best_chip_play(self, team_name, gameweek, value, chip_name, player_name=None):
        self._update_stat("best_chip_play", team_name, gameweek, value, is_highest=True, chip_name=chip_name, player_name=player_name)

    def update_worst_chip_play(self, team_name, gameweek, value, chip_name, player_name=None):
        self._update_stat("worst_chip_play", team_name, gameweek, value, is_highest=False, chip_name=chip_name, player_name=player_name)

    def update_highest_defensive_haul(self, team_name, gameweek, value):
        self._update_stat("highest_defensive_haul", team_name, gameweek, value, is_highest=True)

    def update_highest_attacking_haul(self, team_name, gameweek, value):
        self._update_stat("highest_attacking_haul", team_name, gameweek, value, is_highest=True)

    def update_chip_usage_tally(self, team_name, chip_name):
        if "chip_usage_tally" not in self.stats:
            self.stats["chip_usage_tally"] = {}
        if team_name not in self.stats["chip_usage_tally"]:
            self.stats["chip_usage_tally"][team_name] = {}
        if chip_name not in self.stats["chip_usage_tally"][team_name]:
            self.stats["chip_usage_tally"][team_name][chip_name] = 0
        self.stats["chip_usage_tally"][team_name][chip_name] += 1
        print(f"Updated chip usage tally: {team_name} used {chip_name} (Total: {self.stats['chip_usage_tally'][team_name][chip_name]})")

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

    def update_total_defensive_points_per_manager(self, team_name, defensive_points):
        if "total_defensive_points_per_manager" not in self.stats:
            self.stats["total_defensive_points_per_manager"] = {}
        self.stats["total_defensive_points_per_manager"][team_name] = self.stats["total_defensive_points_per_manager"].get(team_name, 0) + defensive_points
        print(f"Updated total defensive points for {team_name}: {self.stats['total_defensive_points_per_manager'][team_name]}")

    def update_total_attacking_points_per_manager(self, team_name, attacking_points):
        if "total_attacking_points_per_manager" not in self.stats:
            self.stats["total_attacking_points_per_manager"] = {}
        self.stats["total_attacking_points_per_manager"][team_name] = self.stats["total_attacking_points_per_manager"].get(team_name, 0) + attacking_points
        print(f"Updated total attacking points for {team_name}: {self.stats['total_attacking_points_per_manager'][team_name]}")

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

        # New formation stats
        formation = gw_data.get('Formation') # Assuming 'Formation' key exists in gw_data
        if formation:
            self.update_most_common_formations(formation)
            self.update_highest_score_by_formation(formation, team_name, gameweek_int, gw_data['Points'])

        # Update total bank balance per manager
        self.stats["total_bank_balance_per_manager"][team_name] = self.stats["total_bank_balance_per_manager"].get(team_name, 0) + gw_data['Bank Money']

        # Update gameweek count per manager
        self.stats["gameweek_count_per_manager"][team_name] = self.stats["gameweek_count_per_manager"].get(team_name, 0) + 1

        # Update chip-related stats
        chip_used = gw_data.get('Chip Used', "No Chip Used")
        if chip_used != "No Chip Used" and chip_used != "No Chip":
            # Update chip usage tally
            self.update_chip_usage_tally(team_name, chip_used)

            # Update best/worst chip play if it's a chip that affects points
            # Common chips that affect points: BB (Bench Boost), TC (Triple Captain), FH (Free Hit), WC (Wildcard)
            if chip_used in ["BB", "TC", "FH", "WC"]:
                # For best chip play, we use the total points for that gameweek
                self.update_best_chip_play(team_name, gameweek_int, gw_data['Points'], chip_used)

                # For worst chip play, we also use the total points
                # (Note: lower points would be worse for a chip play)
                self.update_worst_chip_play(team_name, gameweek_int, gw_data['Points'], chip_used)

        # Update defensive and attacking haul stats
        self.update_highest_defensive_haul(team_name, gameweek_int, gw_data['Defensive Points'])
        self.update_highest_attacking_haul(team_name, gameweek_int, gw_data['Attacking Points'])
        
        # Update cumulative defensive and attacking points for average calculations
        self.update_total_defensive_points_per_manager(team_name, gw_data['Defensive Points'])
        self.update_total_attacking_points_per_manager(team_name, gw_data['Attacking Points'])

        return self.stats

    def update_most_common_formations(self, formation):
        if "most_common_formations" not in self.stats:
            self.stats["most_common_formations"] = {}
        self.stats["most_common_formations"][formation] = self.stats["most_common_formations"].get(formation, 0) + 1
        print(f"Updated formation count for {formation}: {self.stats['most_common_formations'][formation]}")

    def update_highest_score_by_formation(self, formation, team_name, gameweek, score):
        if "highest_score_by_formation" not in self.stats:
            self.stats["highest_score_by_formation"] = {}
        
        current_highest = self.stats["highest_score_by_formation"].get(formation, {"value": None})
        
        if current_highest["value"] is None or score > current_highest["value"]:
            self.stats["highest_score_by_formation"][formation] = {
                "team": team_name,
                "gameweek": gameweek,
                "value": score
            }
            print(f"Updated highest score for formation {formation}: {score} by {team_name} in GW {gameweek}")

    def save_stats(self):
        save_to_json(self.stats, self.filepath)
        print(f"All-time stats saved to {self.filepath}")