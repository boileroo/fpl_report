from functions.data_operations import fetch_and_save_raw_data, load_data_and_create_mappings, get_formatted_league_name
from functions.report_generation import generate_analysis_report, save_report_to_file, generate_all_time_analysis_report
from functions.data_processing import get_detailed_gw_data, get_differential_king
from functions.all_time_stats import AllTimeStatsManager
import os

import sys

def _parse_arguments():
    if len(sys.argv) != 3:
        print("Usage: python3 main.py <gameweek> <league_id>")
        sys.exit(1)
    
    gameweek_str = sys.argv[1]
    league_id = sys.argv[2]
    
    try:
        gameweek_int = int(gameweek_str)
    except ValueError:
        print(f"Error: Gameweek '{gameweek_str}' must be an integer.")
        sys.exit(1)
        
    return gameweek_str, gameweek_int, league_id

def _initialize_data(gameweek_str, league_id):
    league_data_filepath, player_data_filepath = fetch_and_save_raw_data(gameweek_str, league_id)
    league_data, player_id_to_name, player_id_to_points, player_id_to_position = load_data_and_create_mappings(league_data_filepath, player_data_filepath)
    league_name = get_formatted_league_name(league_data)
    return league_data, player_id_to_name, player_id_to_points, player_id_to_position, league_name

def _process_manager_data(league_data, gameweek_int, player_id_to_name, player_id_to_points, player_id_to_position, all_time_stats_manager):
    for manager_data in league_data['standings']['results']:
        team_name = manager_data['entry_name']
        gw_data_list = get_detailed_gw_data(manager_data, gameweek_int, player_id_to_name, player_id_to_points, player_id_to_position, league_data)[0]
        
        all_time_stats_manager.update_all_stats_for_manager(
            gw_data_list,
            team_name,
            gameweek_int,
            manager_data
        )
        
        _process_autosubs(manager_data, team_name, gameweek_int, player_id_to_name, player_id_to_points, all_time_stats_manager)

def _process_autosubs(manager_data, team_name, gameweek_int, player_id_to_name, player_id_to_points, all_time_stats_manager):
    current_gw_autosubs = [
        sub for sub in manager_data.get('gameweek_data', {}).get(str(gameweek_int), {}).get('automatic_subs', [])
        if sub.get('event') == gameweek_int
    ]
    
    for autosub in current_gw_autosubs:
        player_in_id = autosub.get('element_in')
        if player_in_id:
            player_in_name = player_id_to_name.get(player_in_id, 'Unknown Player')
            player_in_points = player_id_to_points.get(player_in_id, 0)
            all_time_stats_manager.update_best_autosub_cameo(team_name, gameweek_int, player_in_name, player_in_points)

def _generate_reports(gameweek_str, league_name, league_data, player_id_to_name, player_id_to_points, player_id_to_position, differential_king, all_time_stats_manager):
    output_content = generate_analysis_report(gameweek_str, league_data, player_id_to_name, player_id_to_points, player_id_to_position, differential_king)
    save_report_to_file(output_content, gameweek_str, league_name)
    
    generate_all_time_analysis_report(all_time_stats_manager.stats, league_name)


def main():
    gameweek_str, gameweek_int, league_id = _parse_arguments()
    league_data, player_id_to_name, player_id_to_points, player_id_to_position, league_name = _initialize_data(gameweek_str, league_id)
    
    all_time_stats_base_filepath = os.path.join("outputs", league_name, "all_time_stats.json")
    all_time_stats_manager = AllTimeStatsManager(all_time_stats_base_filepath, gameweek_int)
    
    _process_manager_data(league_data, gameweek_int, player_id_to_name, player_id_to_points, player_id_to_position, all_time_stats_manager)
    
    differential_king = get_differential_king(league_data, gameweek_int, player_id_to_name, player_id_to_points)
    all_time_stats_manager.process_differential_king(differential_king)
    
    _generate_reports(gameweek_str, league_name, league_data, player_id_to_name, player_id_to_points, player_id_to_position, differential_king, all_time_stats_manager)

if __name__ == "__main__":
    main()