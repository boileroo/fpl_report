from datetime import datetime
from functions.data_processing import get_detailed_gw_data

def generate_analysis_report(gameweek, mini_league_data, player_id_to_name, player_id_to_points, player_id_to_position, differential_king_queen):
    output = f"Analysis generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # Extract detailed gameweek data for all managers in the mini-league
    for manager_data in mini_league_data['standings']['results']:
        manager_name = manager_data['entry_name']
        gw_data = get_detailed_gw_data(manager_data, int(gameweek), player_id_to_name, player_id_to_points, player_id_to_position, mini_league_data)

        output += f"\nManager: {manager_name}\n"
        output += "-" * 80 + "\n"
        for data in gw_data:
            output += f"Gameweek: {data['Gameweek']}\n"
            output += f"Points: {data['Points']}\n"
            output += f"Rank: {data['Rank']}\n"
            output += f"Captain: {data['Captain']}, {data['Captain Points']} points\n"
            output += f"Vice-Captain: {data['Vice-Captain']}, {data['Vice-Captain Points']} points\n"
            output += f"Transfers: {data['Transfers']}\n"
            output += f"Transfer Cost: {data['Transfer Cost']}\n"
            output += f"Team Value: {data['Team Value']}\n"
            output += f"Points on Bench: {data['Points on Bench']}\n"
            output += f"Bank Money: {data['Bank Money']}\n"
            output += f"Top Scorer: {data['Top Scorer']}, {data['Top Scorer Points']} points{' (on bench)' if not data['Top Scorer Played'] else ''}\n"
            output += f"Underperformer: {data['Underperformer']}, {data['Underperformer Points']} points\n"
            output += f"Formation: {data['Formation']}\n"
            output += f"Defensive Points: {data['Defensive Points']}\n"
            output += f"Attacking Points: {data['Attacking Points']}\n"
            output += f"Chip Used: {data['Chip Used']}\n"
            output += f"Performance vs Avg: {data['Performance vs Avg']}\n"
            output += f"Rank Movement: {data['Rank Movement']}\n"
            output += "-" * 80 + "\n"

    # Extract league standings
    league_standings = mini_league_data.get('standings', {}).get('results', [])
    team_data = [{'Team Name': team['entry_name'], 'Points': team['total']} for team in league_standings]

    output += "\nLeague Standings:\n"
    output += "Team Name,Points\n"
    for team in team_data:
        output += f"{team['Team Name']},{team['Points']}\n"
    
    # Differential King/Queen
    output += "\n## Differential King/Queen\n\n"
    if differential_king_queen:
        output += f"The Differential King/Queen for Gameweek {gameweek} is: \n"
        output += f"Player: {differential_king_queen['player_name']} ({differential_king_queen['points']} points)\n"
        output += f"Owned by: {differential_king_queen['owner']}\n"
    else:
        output += "No Differential King/Queen found for this gameweek (no player owned by only one manager scored points).\n"
    output += "\n"

    return output

import os

def save_report_to_file(output_content, gameweek, league_name):
    output_dir = f"outputs/{league_name}/gameweek_{gameweek}"
    os.makedirs(output_dir, exist_ok=True)
    filepath = f"{output_dir}/gw_analysis.txt"
    with open(filepath, 'w') as file:
        file.write(output_content)
    print(output_content)
    print(f"Analysis saved to {filepath}")

def generate_all_time_analysis_report(all_time_stats, league_name):
    output = f"# All-Time FPL League Records\n\n"
    output += f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    output += "## League Records\n\n"
    output += "| Statistic                | Team Name      | Gameweek | Value      |\n"
    output += "| ------------------------ | -------------- | -------- | ---------- |\n"

    stats_map = {
        "highest_gw_score": "Highest Gameweek Score",
        "lowest_gw_score": "Lowest Gameweek Score",
        "most_points_on_bench": "Most Points on Bench",
        "highest_team_value": "Highest Team Value",
        "biggest_bank_balance": "Biggest Bank Balance",
        "most_captain_points": "Most Captain Points",
        "worst_captain_points": "Worst Captain Points",
        "most_transfers": "Most Transfers",
        "highest_gw_rank": "Highest Gameweek Rank",
        "lowest_gw_rank": "Lowest Gameweek Rank",
        "highest_overall_rank": "Highest Overall Rank",
        "lowest_overall_rank": "Lowest Overall Rank",
        "biggest_rank_drop": "Biggest Rank Drop",
        "biggest_rank_climb": "Biggest Rank Climb",
        "best_autosub_cameo": "Best Autosub Cameo",
        "best_chip_play": "Best Chip Play",
        "worst_chip_play": "Worst Chip Play",
        "highest_defensive_haul": "Highest Defensive Haul (GK+DEF)",
        "highest_attacking_haul": "Highest Attacking Haul (MID+FWD)",
        "narrowest_gw_score_variance": "Mr/Ms Consistency (Narrowest GW Score Variance)",
        "widest_gw_score_variance": "YOLO Award (Widest GW Score Variance)"
    }

    for key, display_name in stats_map.items():
        stat = all_time_stats.get(key)
        
        team_display = "N/A"
        gameweek_display = "N/A"
        value_display = "N/A"
        player_display = ""

        if stat and stat.get('value') is not None:
            value = stat['value']
            team_display = stat['team'] if stat.get('team') is not None else "N/A"
            gameweek_display = stat['gameweek'] if stat.get('gameweek') is not None else "N/A"
            
            if "player" in stat:
                player_display = f" (Player: {stat['player']})"
            
            if "team_value" in key:
                value_display = f"{value:.1f}m"
            elif "rank" in key and (value == float('inf') or value == 0):
                value_display = "N/A"
            elif "captain_points" in key and value == float('inf'):
                value_display = "N/A"
            elif "score" in key and (value == float('inf') or (value == 0 and "lowest" in key)):
                value_display = "N/A"
            elif "rank_drop" in key and value == 0:
                value_display = "N/A"
            elif "rank_climb" in key and value == 0:
                value_display = "N/A"
            elif "chip" in key and (value == 0 and "worst" in key):
                value_display = "N/A"
            else:
                value_display = f"{value:.2f}" # Format variance to 2 decimal places
        
        output += f"| {display_name:<24} | {team_display:<14} | {gameweek_display:<8} | {value_display:<10}{player_display}{' (Chip: ' + stat.get('chip', '') if stat and 'chip' in stat else ''} |\n"

    output += "\n## Captaincy Stats\n\n"
    
    # Total captaincy points accumulated per manager
    if "total_captaincy_points_per_manager" in all_time_stats:
        output += "### Total Captaincy Points Per Manager\n"
        output += "| Manager        | Total Points |\n"
        output += "| -------------- | ------------ |\n"
        sorted_managers = sorted(all_time_stats["total_captaincy_points_per_manager"].items(), key=lambda item: item[1], reverse=True)
        for manager, points in sorted_managers:
            output += f"| {manager:<14} | {points:<12} |\n"
        output += "\n"

    # Most popular captain choices
    if "most_popular_captain_choices" in all_time_stats:
        output += "### Most Popular Captain Choices\n"
        output += "| Player Name    | Times Captained |\n"
        output += "| -------------- | --------------- |\n"
        sorted_players = sorted(all_time_stats["most_popular_captain_choices"].items(), key=lambda item: item[1], reverse=True)
        for player, count in sorted_players:
            output += f"| {player:<14} | {count:<15} |\n"
        output += "\n"

    output += "\n## Bench and Autosub Stats\n\n"

    # Total bench points wasted per manager
    if "total_bench_points_wasted_per_manager" in all_time_stats:
        output += "### Total Bench Points Wasted Per Manager\n"
        output += "| Manager        | Total Points Wasted |\n"
        output += "| -------------- | ------------------- |\n"
        sorted_managers = sorted(all_time_stats["total_bench_points_wasted_per_manager"].items(), key=lambda item: item[1], reverse=True)
        for manager, points in sorted_managers:
            output += f"| {manager:<14} | {points:<19} |\n"
        output += "\n"

    # Most Frugal Manager (Average Bank Left Unused)
    if "total_bank_balance_per_manager" in all_time_stats and "gameweek_count_per_manager" in all_time_stats:
        output += "## Frugality Stats\n\n"
        output += "### Most Frugal Manager (Average Bank Left Unused)\n"
        output += "| Manager        | Average Bank Left Unused |\n"
        output += "| -------------- | ------------------------ |\n"
        
        frugal_managers = {}
        for manager, total_bank in all_time_stats["total_bank_balance_per_manager"].items():
            gameweek_count = all_time_stats["gameweek_count_per_manager"].get(manager, 0)
            if gameweek_count > 0:
                frugal_managers[manager] = total_bank / gameweek_count
            else:
                frugal_managers[manager] = 0 # Handle managers with no gameweek data

        sorted_frugal_managers = sorted(frugal_managers.items(), key=lambda item: item[1], reverse=True)
        for manager, avg_bank in sorted_frugal_managers:
            output += f"| {manager:<14} | {avg_bank:<24.1f} |\n"
        output += "\n"

    output += "\n## Formation Stats\n\n"

    # Most Common Formations
    if "most_common_formations" in all_time_stats:
        output += "### Most Common Formations\n"
        output += "| Formation | Count |\n"
        output += "| --------- | ----- |\n"
        sorted_formations = sorted(all_time_stats["most_common_formations"].items(), key=lambda item: item[1], reverse=True)
        for formation, count in sorted_formations:
            output += f"| {formation:<9} | {count:<5} |\n"
        output += "\n"

    # Highest Score by Formation
    if "highest_score_by_formation" in all_time_stats:
        output += "### Highest Score by Formation\n"
        output += "| Formation | Team Name      | Gameweek | Score |\n"
        output += "| --------- | -------------- | -------- | ----- |\n"
        for formation, data in all_time_stats["highest_score_by_formation"].items():
            output += f"| {formation:<9} | {data['team']:<14} | {data['gameweek']:<8} | {data['value']:<5} |\n"
        output += "\n"

    # Unusual Formations Spotted
    if "unusual_formations_spotted" in all_time_stats and all_time_stats["unusual_formations_spotted"]:
        output += "### Unusual Formations Spotted\n"
        output += "| Formation | Team Name      | Gameweek |\n"
        output += "| --------- | -------------- | -------- |\n"
        # To avoid duplicates in the report, we can use a set of tuples
        # (formation, team, gameweek) to track unique entries.
        # However, the current implementation in all_time_stats.py already appends
        # only if the exact entry is not present. So, we can just iterate.
        for entry in all_time_stats["unusual_formations_spotted"]:
            output += f"| {entry['formation']:<9} | {entry['team']:<14} | {entry['gameweek']:<8} |\n"
        output += "\n"

    # Chip Usage Stats
    if "chip_usage_tally" in all_time_stats and all_time_stats["chip_usage_tally"]:
        output += "\n## Chip Usage Stats\n\n"

        # Chip Usage Tally
        output += "### Chip Usage Tally\n"
        output += "| Manager        | BB | TC | FH | WC |\n"
        output += "| -------------- | -- | -- | -- | -- |\n"

        for manager, chips in all_time_stats["chip_usage_tally"].items():
            bb_count = chips.get("BB", 0)
            tc_count = chips.get("TC", 0)
            fh_count = chips.get("FH", 0)
            wc_count = chips.get("WC", 0)

            output += f"| {manager:<14} | {bb_count:<3} | {tc_count:<3} | {fh_count:<3} | {wc_count:<3} |\n"
        output += "\n"

        # Add defensive/attacking balance stats
        if "total_defensive_points_per_manager" in all_time_stats and "total_attacking_points_per_manager" in all_time_stats and "gameweek_count_per_manager" in all_time_stats:
            output += "\n## Defensive vs Attacking Balance\n\n"
            output += "### Team Balance Comparison\n"
            output += "| Team Name | Avg Defensive Points | Avg Attacking Points | Balance Ratio (D/A) |\n"
            output += "| --------- | -------------------- | -------------------- | ------------------- |\n"

            # Calculate average defensive and attacking points per manager
            defensive_averages = {}
            attacking_averages = {}
            for manager in all_time_stats["total_defensive_points_per_manager"]:
                gameweek_count = all_time_stats["gameweek_count_per_manager"].get(manager, 0)
                if gameweek_count > 0:
                    defensive_averages[manager] = all_time_stats["total_defensive_points_per_manager"][manager] / gameweek_count
                    attacking_averages[manager] = all_time_stats["total_attacking_points_per_manager"][manager] / gameweek_count

            # Most defence-heavy team (highest average defensive points)
            if defensive_averages:
                most_defensive_team = max(defensive_averages.items(), key=lambda x: x[1])

            # Most attack-heavy team (highest average attacking points)
            if attacking_averages:
                most_attacking_team = max(attacking_averages.items(), key=lambda x: x[1])

            # Add the comparison table with all managers
            for manager in sorted(defensive_averages.keys()):
                def_avg = defensive_averages.get(manager, 0)
                att_avg = attacking_averages.get(manager, 0)
                balance_ratio = def_avg / att_avg if att_avg > 0 else float('inf')
                output += f"| {manager} | {def_avg:.2f} | {att_avg:.2f} | {balance_ratio:.2f} |\n"
            output += "\n"

            output += f"### Most Defence-Heavy Team\n"
            output += f"Team: {most_defensive_team[0]}\n"
            output += f"Average Defensive Points (GK+DEF): {most_defensive_team[1]:.2f}\n\n"

            output += f"### Most Attack-Heavy Team\n"
            output += f"Team: {most_attacking_team[0]}\n"
            output += f"Average Attacking Points (MID+FWD): {most_attacking_team[1]:.2f}\n\n"


    output_dir = f"outputs/{league_name}"
    os.makedirs(output_dir, exist_ok=True)
    filepath = f"{output_dir}/all_time_analysis.md"
    with open(filepath, 'w') as file:
        file.write(output)
    print(f"All-time analysis saved to {filepath}")