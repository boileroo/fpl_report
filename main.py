from functions.data_operations import fetch_and_save_raw_data, load_data_and_create_mappings, get_formatted_league_name
from functions.report_generation import generate_analysis_report, save_report_to_file, generate_all_time_analysis_report
from functions.data_processing import get_detailed_gw_data, get_differential_king_queen
from functions.all_time_stats import AllTimeStatsManager
import os

import sys

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 main.py <gameweek> <league_id>")
        sys.exit(1)
    
    gameweek_str = sys.argv[1]
    gameweek_int = int(gameweek_str)
    league_id = sys.argv[2]
    
    mini_league_file, player_data_file = fetch_and_save_raw_data(gameweek_str, league_id)

    mini_league_data, player_id_to_name, player_id_to_points, player_id_to_position = load_data_and_create_mappings(mini_league_file, player_data_file)
    league_name = get_formatted_league_name(mini_league_data)

    # Define the base path for all-time stats file
    all_time_stats_base_filepath = os.path.join("outputs", league_name, "all_time_stats.json")
    
    # Load or create all-time stats for the current gameweek
    all_time_stats_manager = AllTimeStatsManager(all_time_stats_base_filepath, gameweek_int)

    # Update all-time stats for each manager
    for manager_data in mini_league_data['standings']['results']:
        team_name = manager_data['entry_name']
        gw_data = get_detailed_gw_data(manager_data, gameweek_int, player_id_to_name, player_id_to_points, player_id_to_position, mini_league_data)[0]
        
        # Update all-time stats using the centralized function within the manager
        all_time_stats_manager.update_all_stats_for_manager(
            gw_data,
            team_name,
            gameweek_int,
            manager_data
        )
        
        # Best Autosub Cameo (still needs to be handled separately as it's not in gw_data)
        current_gw_autosubs = [
            sub for sub in manager_data['gameweek_data'].get(str(gameweek_int), {}).get('automatic_subs', [])
            if sub.get('event') == gameweek_int
        ]

        for autosub in current_gw_autosubs:
            player_in_id = autosub.get('element_in')
            if player_in_id:
                player_in_name = player_id_to_name.get(player_in_id, 'Unknown Player')
                player_in_points = player_id_to_points.get(player_in_id, 0)
                all_time_stats_manager.update_best_autosub_cameo(team_name, gameweek_int, player_in_name, player_in_points)

    # Save updated all-time stats
    all_time_stats_manager.save_stats()
    
    # Get Differential King/Queen
    differential_king_queen = get_differential_king_queen(mini_league_data, gameweek_int, player_id_to_name, player_id_to_points)

    output_content = generate_analysis_report(gameweek_str, mini_league_data, player_id_to_name, player_id_to_points, player_id_to_position, differential_king_queen)
    save_report_to_file(output_content, gameweek_str, league_name)

    # Generate and save all-time analysis report
    generate_all_time_analysis_report(all_time_stats_manager.stats, league_name)

if __name__ == "__main__":
    main()