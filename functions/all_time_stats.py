import copy
import statistics
from pathlib import Path
from functions.file_operations import load_or_create_all_time_stats, save_to_json

class AllTimeStatsManager:
    def __init__(self, league_name, gameweek):
        self.league_name = league_name
        self.gameweek = gameweek

        self.filepath = self._get_gameweek_filepath(league_name, gameweek)

        print(self.filepath)

        previous_gameweek_stats = {}
        previous_gameweek = gameweek - 1
        if previous_gameweek > 0:
            previous_gw_filepath = self._get_gameweek_filepath(league_name, previous_gameweek)
            previous_gameweek_stats = load_or_create_all_time_stats(str(previous_gw_filepath))

        self.stats = load_or_create_all_time_stats(str(self.filepath))
        cumulative_keys = [
            "total_captaincy_points_per_manager",
            "most_popular_captain_choices",
            "total_bench_points_wasted_per_manager",
            "total_bank_balance_per_manager",
            "gameweek_count_per_manager",
            "most_common_formations",
            "highest_score_by_formation",
            "chip_usage_tally",
            "total_defensive_points_per_manager",
            "total_attacking_points_per_manager",
            "gw_scores_per_manager",
            "narrowest_gw_score_variance",
            "widest_gw_score_variance",
            "highest_league_rank_per_manager",
            "lowest_league_rank_per_manager",
            "differential_king_per_gameweek"
        ]

        for key in cumulative_keys:
            if key in previous_gameweek_stats:
                self.stats[key] = copy.deepcopy(previous_gameweek_stats[key])
            else:
                self.stats[key] = {}

        self._ensure_output_directory_exists()

    @staticmethod
    def _generate_gameweek_filename(base_filename, gameweek, extension):
        return f"{base_filename}_gw_{gameweek}{extension}"

    @staticmethod
    def _get_gameweek_filepath(league_name, gameweek, base_filename="all_time_stats", extension=".json"):
        filename = AllTimeStatsManager._generate_gameweek_filename(base_filename, gameweek, extension)
        return Path("outputs") / league_name / f"gameweek_{gameweek}" / filename

    def _ensure_output_directory_exists(self):
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    def _update_stat(self, stat_key, team_name, gameweek, value, is_highest=True, player_name=None, chip_name=None):
        current_stat = self.stats.get(stat_key, {"value": None})
        current_value = current_stat["value"]
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
            self.stats[stat_key] = {
                "team": team_name,
                "gameweek": gameweek,
                "value": value
            }
            if player_name:
                self.stats[stat_key]["player"] = player_name
            if chip_name:
                self.stats[stat_key]["chip"] = chip_name

    def _update_manager_league_rank_stat(self, stat_key, team_name, gameweek, value, is_highest=True):
        manager_stat = self.stats.get(stat_key, {}) # Get the dictionary for all managers for this stat
        current_manager_record = manager_stat.get(team_name, {"value": None})
        current_value = current_manager_record["value"]
        updated = False

        if current_value is None: # Initialize if not set
            updated = True
        elif is_highest: # For 'lowest_league_rank_per_manager' (higher rank number is worse/higher)
            if value > current_value:
                updated = True
        else: # For 'highest_league_rank_per_manager' (lower rank number is better/lower)
            if value < current_value:
                updated = True

        if updated:
            manager_stat[team_name] = {
                "gameweek": gameweek,
                "value": value
            }
            self.stats[stat_key] = manager_stat # Ensure the updated manager_stat is saved back

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
        self.stats["chip_usage_tally"].setdefault(team_name, {}).setdefault(chip_name, 0)
        self.stats["chip_usage_tally"][team_name][chip_name] += 1

    def update_highest_overall_gameweek_rank(self, team_name, gameweek, value):
        self._update_stat("highest_overall_gameweek_rank", team_name, gameweek, value, is_highest=False) # Lower rank is better

    def update_lowest_overall_gameweek_rank(self, team_name, gameweek, value):
        self._update_stat("lowest_overall_gameweek_rank", team_name, gameweek, value, is_highest=True) # Higher rank is worse

    def update_highest_overall_rank(self, team_name, gameweek, value):
        self._update_stat("highest_overall_rank", team_name, gameweek, value, is_highest=False) # Lower rank is better

    def update_lowest_overall_rank(self, team_name, gameweek, value):
        self._update_stat("lowest_overall_rank", team_name, gameweek, value, is_highest=True) # Higher rank is worse

    def update_biggest_league_rank_drop(self, team_name, gameweek, value):
        self._update_stat("biggest_league_rank_drop", team_name, gameweek, value, is_highest=False)

    def update_biggest_league_rank_climb(self, team_name, gameweek, value):
        self._update_stat("biggest_league_rank_climb", team_name, gameweek, value, is_highest=True)

    def update_highest_league_rank_per_manager(self, team_name, gameweek, value):
        self._update_manager_league_rank_stat("highest_league_rank_per_manager", team_name, gameweek, value, is_highest=False) # Lower rank number is better

    def update_lowest_league_rank_per_manager(self, team_name, gameweek, value):
        self._update_manager_league_rank_stat("lowest_league_rank_per_manager", team_name, gameweek, value, is_highest=True) # Higher rank number is worse

    def update_total_captaincy_points_per_manager(self, team_name, captain_points):
        self.stats["total_captaincy_points_per_manager"][team_name] = self.stats["total_captaincy_points_per_manager"].get(team_name, 0) + captain_points

    def update_most_popular_captain_choices(self, player_name):
        self.stats["most_popular_captain_choices"][player_name] = self.stats["most_popular_captain_choices"].get(player_name, 0) + 1

    def update_total_bench_points_wasted_per_manager(self, team_name, bench_points):
        self.stats["total_bench_points_wasted_per_manager"][team_name] = self.stats["total_bench_points_wasted_per_manager"].get(team_name, 0) + bench_points

    def update_best_autosub_cameo(self, team_name, gameweek, player_name, points):
        self._update_stat("best_autosub_cameo", team_name, gameweek, points, is_highest=True, player_name=player_name)

    def update_total_defensive_points_per_manager(self, team_name, defensive_points):
        self.stats["total_defensive_points_per_manager"][team_name] = self.stats["total_defensive_points_per_manager"].get(team_name, 0) + defensive_points

    def update_total_attacking_points_per_manager(self, team_name, attacking_points):
        self.stats["total_attacking_points_per_manager"][team_name] = self.stats["total_attacking_points_per_manager"].get(team_name, 0) + attacking_points

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
        self.update_highest_overall_rank(team_name, gameweek_int, gw_data['Overall Rank']) # Lower rank is better
        self.update_lowest_overall_rank(team_name, gameweek_int, gw_data['Overall Rank']) # Higher rank is worse
        self.update_highest_overall_gameweek_rank(team_name, gameweek_int, gw_data['Overall Gameweek Rank']) # Lower rank is better
        self.update_lowest_overall_gameweek_rank(team_name, gameweek_int, gw_data['Overall Gameweek Rank']) # Higher rank is worse

        # Update league rank movement stats
        # For Gameweek 1, rank changes should be 0
        if self.gameweek == 1:
            league_rank_movement_for_stats = 0
        else:
            league_rank_movement_for_stats = gw_data.get('League Rank Movement', 0)
            
        if league_rank_movement_for_stats < 0: # Rank drop
            self.update_biggest_league_rank_drop(team_name, gameweek_int, league_rank_movement_for_stats)
        elif league_rank_movement_for_stats > 0: # Rank climb
            self.update_biggest_league_rank_climb(team_name, gameweek_int, league_rank_movement_for_stats)

        self.update_highest_league_rank_per_manager(team_name, gameweek_int, gw_data['League Rank']) # Lower rank is better
        self.update_lowest_league_rank_per_manager(team_name, gameweek_int, gw_data['League Rank'])  # Higher rank is worse

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

        # Calculate and update GW score variance if enough data points exist
        manager_gw_scores = self.stats["gw_scores_per_manager"].get(team_name, [])
        if len(manager_gw_scores) >= 2: # Need at least 2 scores for variance
            gw_variance = statistics.variance(manager_gw_scores)
            self.update_narrowest_gw_score_variance(team_name, gameweek_int, gw_variance)
            self.update_widest_gw_score_variance(team_name, gameweek_int, gw_variance)

        # Accumulate gameweek scores for variance calculation
        self.stats["gw_scores_per_manager"].setdefault(team_name, []).append(gw_data['Points'])

        return self.stats

    def process_differential_king(self, differential_king_data):
        """
        Processes and updates the differential king for the current gameweek.
        Accepts data directly from get_differential_king in data_processing.py
        """
        if differential_king_data:
            self.update_differential_king_per_gameweek(
                gameweek=self.gameweek,
                player_name=differential_king_data['player_name'],
                points=differential_king_data['points'],
                team_name=differential_king_data['owner']
            )

    def update_differential_king_per_gameweek(self, gameweek, player_name, points, team_name):
        """
        Updates the differential king stat for a specific gameweek.
        The differential king is the highest scoring differential player (owned by only one manager) of the gameweek.
        """
        # Ensure the differential_king_per_gameweek structure exists
        if "differential_king_per_gameweek" not in self.stats:
            self.stats["differential_king_per_gameweek"] = {}
        
        # Check if this gameweek's differential king is already set or if the new one has more points
        current_differential_king = self.stats["differential_king_per_gameweek"].get(str(gameweek))
        
        updated = False
        if current_differential_king is None: # No differential king yet for this gameweek
            updated = True
        elif points > current_differential_king["points"]: # New player has more points
            updated = True
            
        if updated:
            self.stats["differential_king_per_gameweek"][str(gameweek)] = {
                "player": player_name,
                "points": points,
                "team": team_name
            }

    def update_narrowest_gw_score_variance(self, team_name, gameweek, variance):
        self._update_stat("narrowest_gw_score_variance", team_name, gameweek, variance, is_highest=False)
        
    def update_widest_gw_score_variance(self, team_name, gameweek, variance):
        self._update_stat("widest_gw_score_variance", team_name, gameweek, variance, is_highest=True)

    def update_most_common_formations(self, formation):
        self.stats["most_common_formations"][formation] = self.stats["most_common_formations"].get(formation, 0) + 1

    def update_highest_score_by_formation(self, formation, team_name, gameweek, score):
        
        current_highest = self.stats["highest_score_by_formation"].get(formation, {"value": None})
        
        if current_highest["value"] is None or score > current_highest["value"]:
            self.stats["highest_score_by_formation"][formation] = {
                "team": team_name,
                "gameweek": gameweek,
                "value": score
            }

    def save_stats(self):
        save_to_json(self.stats, str(self.filepath))