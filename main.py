from functions.data_operations import fetch_raw_data, create_mappings
from functions.report_generation import generate_reports
from functions.data_processing import process_gameweek_for_league, get_differential_king
from functions.all_time_stats import AllTimeStatsManager
import os

import sys

def _parse_arguments():
    if len(sys.argv) != 3:
        print("Usage: python3 main.py <gameweek> <league_id>")
        sys.exit(1)
    
    gameweek = sys.argv[1]
    league_id = sys.argv[2]

    return int(gameweek), str(league_id)

def _initialize_data(league_id, gameweek,):
    league_data_filepath, game_data_filepath = fetch_raw_data(league_id, gameweek)
    league_data, player_data = create_mappings(league_data_filepath, game_data_filepath)
    return league_data, player_data

def main():
    gameweek, league_id = _parse_arguments()
    league_data, player_data = _initialize_data(league_id, gameweek)

    all_time_stats_manager = AllTimeStatsManager(league_data['name'], gameweek)
    
    process_gameweek_for_league(league_data, player_data, gameweek, all_time_stats_manager)
    
    differential_king = get_differential_king(league_data, gameweek, player_data)
    all_time_stats_manager.process_differential_king(differential_king)
    
    generate_reports(league_data, player_data, gameweek, differential_king, all_time_stats_manager)
    all_time_stats_manager.save_stats()

if __name__ == "__main__":
    main()