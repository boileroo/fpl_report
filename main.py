from functions.data_operations import fetch_raw_data, create_mappings
from functions.report_generation import generate_reports
from functions.data_processing import process_gameweek_for_league, get_differential_king
from functions.all_time_stats import AllTimeStatsManager
import os

import sys

def _parse_arguments():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <gameweek> [league_id1] [league_id2] ...")
        sys.exit(1)
    
    gameweek = sys.argv[1]
    
    # If no league IDs provided, use fallback
    if len(sys.argv) == 2:
        league_ids = [1523783, 952600]
    else:
        league_ids = [int(arg) for arg in sys.argv[2:]]

    return int(gameweek), league_ids

def _initialize_data(league_id, gameweek,):
    league_data_filepath, game_data_filepath = fetch_raw_data(league_id, gameweek)
    league_data, player_data = create_mappings(league_data_filepath, game_data_filepath)
    return league_data, player_data

def main():
    gameweek, league_ids = _parse_arguments()
    
    for league_id in league_ids:
        league_data, player_data = _initialize_data(league_id, gameweek)

        all_time_stats_manager = AllTimeStatsManager(league_data['name'], gameweek)
        
        process_gameweek_for_league(league_data, player_data, gameweek, all_time_stats_manager)
        generate_reports(league_data, player_data, gameweek, all_time_stats_manager)

        all_time_stats_manager.save_stats()

if __name__ == "__main__":
    main()