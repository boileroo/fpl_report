from functions.data_operations import fetch_and_save_raw_data, load_data_and_create_mappings, get_formatted_league_name
from functions.report_generation import generate_analysis_report, save_report_to_file, generate_all_time_analysis_report
from functions.data_processing import get_detailed_gw_data
from functions.all_time_stats import AllTimeStatsManager
import os

import sys

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 main.py <gameweek> <league_id>")
        sys.exit(1)
    
    gameweek = sys.argv[1]
    league_id = sys.argv[2]
    
    mini_league_file, player_data_file = fetch_and_save_raw_data(gameweek, league_id)

    mini_league_data, player_id_to_name, player_id_to_points, player_id_to_position = load_data_and_create_mappings(mini_league_file, player_data_file)
    league_name = get_formatted_league_name(mini_league_data)

    # Define the path for all-time stats file
    all_time_stats_filepath = os.path.join("outputs", league_name, "all_time_stats.json")
    
    # Load or create all-time stats
    all_time_stats_manager = AllTimeStatsManager(all_time_stats_filepath)

    # Update all-time stats for each manager
    for manager_data in mini_league_data['standings']['results']:
        team_name = manager_data['entry_name'] # Assuming team name is the same as manager name for now
        gameweek_int = int(gameweek)
        gw_data = get_detailed_gw_data(manager_data, gameweek_int, player_id_to_name, player_id_to_points, player_id_to_position, mini_league_data)[0]
        all_time_stats_manager.update_highest_gw_score(team_name, gameweek_int, gw_data['Points'])
        all_time_stats_manager.update_lowest_gw_score(team_name, gameweek_int, gw_data['Points'])
        all_time_stats_manager.update_most_points_on_bench(team_name, gameweek_int, gw_data['Points on Bench'])
        all_time_stats_manager.update_highest_team_value(team_name, gameweek_int, gw_data['Team Value'])
        all_time_stats_manager.update_most_captain_points(team_name, gameweek_int, gw_data['Captain Points'], gw_data['Captain'])
        all_time_stats_manager.update_worst_captain_points(team_name, gameweek_int, gw_data['Captain Points'], gw_data['Captain'])
        all_time_stats_manager.update_total_captaincy_points_per_manager(team_name, gw_data['Captain Points'])
        all_time_stats_manager.update_most_popular_captain_choices(gw_data['Captain'])
        all_time_stats_manager.update_total_bench_points_wasted_per_manager(team_name, gw_data['Points on Bench'])
        all_time_stats_manager.update_most_transfers(team_name, gameweek_int, gw_data['Transfers'])

        all_time_stats_manager.update_highest_gw_rank(team_name, gameweek_int, gw_data['Rank'])
        all_time_stats_manager.update_lowest_gw_rank(team_name, gameweek_int, gw_data['Rank'])
        all_time_stats_manager.update_highest_overall_rank(team_name, gameweek_int, manager_data['manager_details']['summary_overall_rank'])
        all_time_stats_manager.update_lowest_overall_rank(team_name, gameweek_int, manager_data['manager_details']['summary_overall_rank'])

        rank_change = gw_data.get('Rank Movement', 0)
        if rank_change < 0:
            all_time_stats_manager.update_biggest_rank_drop(team_name, gameweek_int, abs(rank_change))
        elif rank_change > 0:
            all_time_stats_manager.update_biggest_rank_climb(team_name, gameweek_int, rank_change)

        # Best Autosub Cameo (for the current gameweek being processed)
        # The 'automatic_subs' are part of the manager's history, not directly in gw_data['picks']
        # We need to check manager_data['history']['automatic_subs'] for the current gameweek
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
    
    output_content = generate_analysis_report(gameweek, mini_league_data, player_id_to_name, player_id_to_points, player_id_to_position)
    save_report_to_file(output_content, gameweek, league_name)

    # Generate and save all-time analysis report
    generate_all_time_analysis_report(all_time_stats_manager.stats, league_name)

if __name__ == "__main__":
    main()