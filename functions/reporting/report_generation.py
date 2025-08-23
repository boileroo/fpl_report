import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from functions.processing.data_processing import get_detailed_gw_data, get_differential_king
from functions.exceptions import ReportGenerationError
from functions.config import OUTPUT_BASE_DIR, GW_ANALYSIS_FILENAME, ALL_TIME_STATS_FILENAME

def generate_reports(league_data: Dict[str, Any], player_data: Dict[int, Dict[str, Any]], gameweek: int, all_time_stats_manager: Any) -> None:
    try:
        league_name = league_data['name']
        differential_king = get_differential_king(league_data, gameweek, player_data)
        generate_gameweek_analysis_report(league_data, player_data, gameweek, differential_king, league_name)
        generate_all_time_analysis_report(all_time_stats_manager.stats, league_name)
    except Exception as e:
        raise ReportGenerationError(
            f"Error generating reports for league {league_data.get('name', 'unknown')}, gameweek {gameweek}",
            report_type="general"
        ) from e


def generate_gameweek_analysis_report(league_data: Dict[str, Any], player_data: Dict[int, Dict[str, Any]], gameweek: int, differential_king: Optional[Dict[str, Any]], league_name: str) -> None:
    try:
        output = f"League: {league_name}\n"
        output += f"Analysis generated on: {datetime.now().strftime('%Y-%m-%d')}\n\n"

        for entry in league_data.get('standings', {}).get('results', []):
            manager_name = entry.get('entry_name', 'Unknown Manager')
            
            try:
                gw_data = get_detailed_gw_data(league_data, entry, player_data, gameweek)
            except Exception as e:
                output += f"\nManager: {manager_name} (Error processing gameweek data: {str(e)})\n"
                output += "-" * 80 + "\n"
                continue

            if not gw_data:
                output += f"\nManager: {manager_name} (No Gameweek {gameweek} data available)\n"
                output += "-" * 80 + "\n"
                continue

            try:
                data = gw_data[0]
                output += f"\nManager: {manager_name}\n"
                output += "-" * 80 + "\n"

                output += f"Gameweek: {data.get('Gameweek', 'N/A')}\n"
                output += f"Points: {data.get('Points', 'N/A')}\n"
                output += f"Overall Gameweek Rank: {data.get('Overall Gameweek Rank', 'N/A')}\n"
                output += f"Overall Rank: {data.get('Overall Rank', 'N/A')}\n"
                output += f"League Rank: {data.get('League Rank', 'N/A')}\n"
                output += f"League Rank Movement: {data.get('League Rank Movement', 'N/A')}\n"
                output += f"Captain: {data.get('Captain', 'N/A')}, {data.get('Captain Points', 'N/A')} points\n"
                output += f"Vice-Captain: {data.get('Vice-Captain', 'N/A')}, {data.get('Vice-Captain Points', 'N/A')} points\n"
                output += f"Transfers: {data.get('Transfers', 'N/A')}\n"
                output += f"Transfer Cost: {data.get('Transfer Cost', 'N/A')}\n"
                output += f"Team Value: {data.get('Team Value', 'N/A')}\n"
                output += f"Points on Bench: {data.get('Points on Bench', 'N/A')}\n"
                output += f"Bank Money: {data.get('Bank Money', 'N/A')}\n"
                output += f"Top Scorer: {data.get('Top Scorer', 'N/A')}, {data.get('Top Scorer Points', 'N/A')} points{' (on bench)' if not data.get('Top Scorer Played', True) else ''}\n"
                output += f"Underperformer: {data.get('Underperformer', 'N/A')}, {data.get('Underperformer Points', 'N/A')} points\n"
                output += f"Formation: {data.get('Formation', 'N/A')}\n"
                output += f"Defensive Points: {data.get('Defensive Points', 'N/A')}\n"
                output += f"Attacking Points: {data.get('Attacking Points', 'N/A')}\n"
                output += f"Chip Used: {data.get('Chip Used', 'N/A')}\n"
                output += f"Performance vs League Avg: {data.get('Performance vs Avg', 'N/A')}\n"
                
                # Add autosub information
                autosub_details = data.get('autosub_details', [])
                autosub_points = data.get('autosub_points', 0)
                
                output += "\nAutosubs:\n"
                if autosub_details:
                    output += f"  Points gained from autosubs: {autosub_points}\n"
                    for autosub in autosub_details:
                        player_in = autosub.get('player_in_name', 'Unknown')
                        player_out = autosub.get('player_out_name', 'Unknown')
                        points_gained = autosub.get('points_gained', 0)
                        output += f"  Substituted {player_out} → {player_in} (+{points_gained} points)\n"
                else:
                    output += "  No autosubs made this gameweek\n"
                
                output += "-" * 80 + "\n"
            except Exception as e:
                output += f"\nManager: {manager_name} (Error processing data: {str(e)})\n"
                output += "-" * 80 + "\n"
                continue

        # Extract league standings
        try:
            league_standings = league_data.get('standings', {}).get('results', [])
            team_data = [{'Team Name': team.get('entry_name', 'Unknown'), 'Points': team.get('total', 0)} for team in league_standings]

            output += "\nLeague Standings:\n"
            output += "Team Name,Points\n"
            for team in team_data:
                output += f"{team['Team Name']},{team['Points']}\n"
        except Exception as e:
            output += f"\nError processing league standings: {str(e)}\n"

        # New Entries
        try:
            new_entries = league_data.get('new_entries', {}).get('results', [])
            if new_entries:
                output += "\n## New Entries\n"
                for entry in new_entries:
                    output += f"- {entry.get('entry_name', 'Unknown Entry')}\n"
                output += "\n"
        except Exception as e:
            output += f"\nError processing new entries: {str(e)}\n"
        
        # Differential King
        output += "\n## Differential King\n\n"
        if differential_king:
            try:
                output += f"The Differential King for Gameweek {gameweek} is: \n"
                output += f"Player: {differential_king.get('player_name', 'Unknown Player')} ({differential_king.get('points', 0)} points)\n"
                output += f"Owned by: {differential_king.get('owner', 'Unknown Owner')}\n"
            except Exception as e:
                output += f"Error processing differential king: {str(e)}\n"
        else:
            output += "No Differential King found for this gameweek (no player owned by only one manager scored points).\n"
        output += "\n"

        output_dir = f"{OUTPUT_BASE_DIR}/{league_name}/gameweek_{gameweek}"
        os.makedirs(output_dir, exist_ok=True)
        filepath = f"{output_dir}/{GW_ANALYSIS_FILENAME}"
        with open(filepath, 'w') as file:
            file.write(output)
        print(f"Analysis saved to {filepath}")
    except Exception as e:
        raise ReportGenerationError(
            f"Error generating gameweek analysis report for league {league_name}, gameweek {gameweek}",
            report_type="gameweek_analysis"
        ) from e


def generate_all_time_analysis_report(all_time_stats: Dict[str, Any], league_name: str) -> None:
    try:
        output = f"# All-Time League Records for: {league_name}\n\n"
        output += f"Last updated: {datetime.now().strftime('%Y-%m-%d')}\n\n"
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
            "highest_overall_gameweek_rank": "Highest Overall Gameweek Rank",
            "lowest_overall_gameweek_rank": "Lowest Overall Gameweek Rank",
            "highest_overall_rank": "Highest Overall Rank",
            "lowest_overall_rank": "Lowest Overall Rank",
            "biggest_league_rank_drop": "Biggest League Rank Drop",
            "biggest_league_rank_climb": "Biggest League Rank Climb",
            "best_autosub_cameo": "Best Autosub Cameo",
            "best_chip_play": "Best Chip Play",
            "worst_chip_play": "Worst Chip Play",
            "highest_defensive_haul": "Highest Defensive Haul (GK+DEF)",
            "highest_attacking_haul": "Highest Attacking Haul (MID+FWD)",
            "narrowest_gw_score_variance": "Mr/Ms Consistency (Narrowest GW Score Variance)",
            "widest_gw_score_variance": "YOLO Award (Widest GW Score Variance)"
        }

        for key, display_name in stats_map.items():
            try:
                stat = all_time_stats.get("records", {}).get(key)
                
                team_display = "N/A"
                gameweek_display = "N/A"
                value_display = "N/A"
                player_display = ""
                chip_display = ""

                if stat and stat.get('value') is not None:
                    value = stat['value']
                    team_display = stat.get('team', 'N/A') if stat.get('team') is not None else "N/A"
                    gameweek_display = stat.get('gameweek', 'N/A') if stat.get('gameweek') is not None else "N/A"
                    
                    if "player" in stat:
                        player_display = f" (Player: {stat['player']})"
                    
                    if "chip" in stat and stat['chip'] not in ["No Chip Used", "No Chip", None]:
                        chip_display = f" (Chip: {stat['chip']})"
                    
                    if "team_value" in key:
                        value_display = f"{value:.1f}m"
                    elif "rank" in key and (value == float('inf') or value == 0):
                        value_display = "N/A"
                    elif "captain_points" in key and value == float('inf'):
                        value_display = "N/A"
                    elif "score" in key and (value == float('inf') or (value == 0 and "lowest" in key)):
                        value_display = "N/A"
                    elif "league_rank_drop" in key and value == float('inf'):
                        value_display = "N/A"
                    elif "league_rank_climb" in key and value == 0:
                        value_display = "N/A"
                    elif "worst_captain_points" in key and value == float('inf'):
                        value_display = "N/A"
                    elif "worst_chip_play" in key and value == float('inf'):
                        value_display = "N/A"
                    elif key == "highest_overall_gameweek_rank" and value == float('inf'):
                        value_display = "N/A"
                    elif key == "highest_overall_rank" and value == float('inf'):
                        value_display = "N/A"
                    elif key == "narrowest_gw_score_variance" and value == float('inf'):
                        value_display = "N/A"
                    else:
                        if "variance" in key and value != float('inf'):
                            value_display = f"{value:.2f}"
                        elif "variance" in key and value == float('inf'):
                            value_display = "N/A"
                        else:
                            value_display = str(value)
                
                output += f"| {display_name:<24} | {team_display:<14} | {gameweek_display:<8} | {value_display:<10}{player_display}{chip_display} |\n"
            except Exception as e:
                output += f"| {display_name:<24} | Error processing stat | N/A      | N/A        |\n"

        output += "\n## League Rank History\n\n"
        # Highest/Lowest League Rank per Manager
        try:
            if "highest_league_rank" in all_time_stats.get("manager_records", {}) and all_time_stats["manager_records"]["highest_league_rank"]:
                output += "### Highest (Best) League Rank Per Manager\n"
                output += "| Manager        | Best Rank | Gameweek |\n"
                output += "| -------------- | --------- | -------- |\n"
                sorted_managers = sorted(all_time_stats["manager_records"]["highest_league_rank"].items(), key=lambda item: item[1]['value'])
                for manager, data in sorted_managers:
                    output += f"| {manager:<14} | {data.get('value', 'N/A'):<9} | {data.get('gameweek', 'N/A'):<8} |\n"
                output += "\n"
        except Exception as e:
            output += f"Error processing highest league rank data: {str(e)}\n\n"

        try:
            if "lowest_league_rank" in all_time_stats.get("manager_records", {}) and all_time_stats["manager_records"]["lowest_league_rank"]:
                output += "### Lowest (Worst) League Rank Per Manager\n"
                output += "| Manager        | Worst Rank | Gameweek |\n"
                output += "| -------------- | ---------- | -------- |\n"
                sorted_managers = sorted(all_time_stats["manager_records"]["lowest_league_rank"].items(), key=lambda item: item[1]['value'], reverse=True)
                for manager, data in sorted_managers:
                    output += f"| {manager:<14} | {data.get('value', 'N/A'):<10} | {data.get('gameweek', 'N/A'):<8} |\n"
                output += "\n"
        except Exception as e:
            output += f"Error processing lowest league rank data: {str(e)}\n\n"

        # Differential King per Gameweek
        try:
            if "differential_king_per_gameweek" in all_time_stats and all_time_stats["differential_king_per_gameweek"]:
                output += "\n## Differential King Per Gameweek\n"
                output += "| Gameweek | Player         | Points | Team           |\n"
                output += "| -------- | -------------- | ------ | -------------- |\n"
                
                # Sort by gameweek in ascending order
                sorted_gameweeks = sorted(all_time_stats["differential_king_per_gameweek"].items(), key=lambda item: int(item[0]))
                
                for gameweek, data in sorted_gameweeks:
                    output += f"| {gameweek:<8} | {data.get('player', 'N/A'):<14} | {data.get('points', 'N/A'):<6} | {data.get('team', 'N/A'):<14} |\n"
                output += "\n"
        except Exception as e:
            output += f"Error processing differential king data: {str(e)}\n\n"

        output += "\n## Captaincy Stats\n\n"
        
        # Total captaincy points accumulated per manager
        try:
            if "captaincy_points" in all_time_stats.get("cumulative", {}):
                output += "### Total Captaincy Points Per Manager\n"
                output += "| Manager        | Total Points |\n"
                output += "| -------------- | ------------ |\n"
                sorted_managers = sorted(all_time_stats["cumulative"]["captaincy_points"].items(), key=lambda item: item[1], reverse=True)
                for manager, points in sorted_managers:
                    output += f"| {manager:<14} | {points:<12} |\n"
                output += "\n"
        except Exception as e:
            output += f"Error processing captaincy points data: {str(e)}\n\n"

        # Most popular captain choices
        try:
            if "captain_choices" in all_time_stats.get("counts", {}):
                output += "### Most Popular Captain Choices\n"
                output += "| Player Name    | Times Captained |\n"
                output += "| -------------- | --------------- |\n"
                sorted_players = sorted(all_time_stats["counts"]["captain_choices"].items(), key=lambda item: item[1], reverse=True)
                for player, count in sorted_players:
                    output += f"| {player:<14} | {count:<15} |\n"
                output += "\n"
        except Exception as e:
            output += f"Error processing captain choices data: {str(e)}\n\n"

        output += "\n## Bench and Autosub Stats\n\n"

        # Total bench points wasted per manager
        try:
            if "bench_points" in all_time_stats.get("cumulative", {}):
                output += "### Total Bench Points Wasted Per Manager\n"
                output += "| Manager        | Total Points Wasted |\n"
                output += "| -------------- | ------------------- |\n"
                sorted_managers = sorted(all_time_stats["cumulative"]["bench_points"].items(), key=lambda item: item[1], reverse=True)
                for manager, points in sorted_managers:
                    output += f"| {manager:<14} | {points:<19} |\n"
                output += "\n"
        except Exception as e:
            output += f"Error processing bench points data: {str(e)}\n\n"

        # Most Frugal Manager (Average Bank Left Unused)
        try:
            if "bank_balance" in all_time_stats.get("cumulative", {}) and "gameweek_participation" in all_time_stats.get("counts", {}):
                output += "## Frugality Stats\n\n"
                output += "### Most Frugal Manager (Average Bank Left Unused)\n"
                output += "| Manager        | Average Bank Left Unused |\n"
                output += "| -------------- | ------------------------ |\n"
                
                frugal_managers = {}
                for manager, total_bank in all_time_stats["cumulative"]["bank_balance"].items():
                    gameweek_count = all_time_stats["counts"]["gameweek_participation"].get(manager, 0)
                    if gameweek_count > 0:
                        frugal_managers[manager] = total_bank / gameweek_count
                    else:
                        frugal_managers[manager] = 0

                sorted_frugal_managers = sorted(frugal_managers.items(), key=lambda item: item[1], reverse=True)
                for manager, avg_bank in sorted_frugal_managers:
                    output += f"| {manager:<14} | {avg_bank:<24.1f} |\n"
                output += "\n"
        except Exception as e:
            output += f"Error processing frugality stats data: {str(e)}\n\n"

        output += "\n## Formation Stats\n\n"

        # Most Common Formations
        try:
            if "formations" in all_time_stats.get("counts", {}):
                output += "### Most Common Formations\n"
                output += "| Formation | Count |\n"
                output += "| --------- | ----- |\n"
                sorted_formations = sorted(all_time_stats["counts"]["formations"].items(), key=lambda item: item[1], reverse=True)
                for formation, count in sorted_formations:
                    output += f"| {formation:<9} | {count:<5} |\n"
                output += "\n"
        except Exception as e:
            output += f"Error processing formation data: {str(e)}\n\n"

        # Highest Score by Formation
        try:
            if "highest_score_by_formation" in all_time_stats.get("formations", {}):
                output += "### Highest Score by Formation\n"
                output += "| Formation | Team Name      | Gameweek | Score |\n"
                output += "| --------- | -------------- | -------- | ----- |\n"
                for formation, data in all_time_stats["formations"]["highest_score_by_formation"].items():
                    output += f"| {formation:<9} | {data.get('team', 'N/A'):<14} | {data.get('gameweek', 'N/A'):<8} | {data.get('value', 'N/A'):<5} |\n"
                output += "\n"
        except Exception as e:
            output += f"Error processing highest score by formation data: {str(e)}\n\n"

        # Chip Usage Stats
        try:
            if "chip_usage" in all_time_stats.get("counts", {}) and all_time_stats["counts"]["chip_usage"]:
                output += "\n## Chip Usage Stats\n\n"

                # Chip Usage Tally
                output += "### Chip Usage Tally\n"
                output += "| Manager        | BB | TC | FH | WC |\n"
                output += "| -------------- | -- | -- | -- | -- |\n"

                for manager, chips in all_time_stats["counts"]["chip_usage"].items():
                    bb_count = chips.get("BB", 0)
                    tc_count = chips.get("TC", 0)
                    fh_count = chips.get("FH", 0)
                    wc_count = chips.get("WC", 0)

                    output += f"| {manager:<14} | {bb_count:<3} | {tc_count:<3} | {fh_count:<3} | {wc_count:<3} |\n"
                output += "\n"
        except Exception as e:
            output += f"Error processing chip usage data: {str(e)}\n\n"

        # Total autosub points per manager
        try:
            if "autosub_points" in all_time_stats.get("cumulative", {}):
                output += "\n## Autosub Stats\n\n"
                output += "### Total Autosub Points Per Manager\n"
                output += "| Manager        | Total Autosub Points |\n"
                output += "| -------------- | -------------------- |\n"
                sorted_managers = sorted(all_time_stats["cumulative"]["autosub_points"].items(), key=lambda item: item[1], reverse=True)
                for manager, points in sorted_managers:
                    output += f"| {manager:<14} | {points:<20} |\n"
                output += "\n"
        except Exception as e:
            output += f"Error processing autosub points data: {str(e)}\n\n"

        # Add defensive/attacking balance stats
        try:
            if ("defensive_points" in all_time_stats.get("cumulative", {}) and 
                "attacking_points" in all_time_stats.get("cumulative", {}) and 
                "gameweek_participation" in all_time_stats.get("counts", {})):
                output += "\n## Defensive vs Attacking Balance\n\n"
                output += "### Team Balance Comparison\n"
                output += "| Team Name | Avg Defensive Points | Avg Attacking Points | Balance Ratio (D/A) |\n"
                output += "| --------- | -------------------- | -------------------- | ------------------- |\n"

                # Calculate average defensive and attacking points per manager
                defensive_averages = {}
                attacking_averages = {}
                for manager in all_time_stats["cumulative"]["defensive_points"]:
                    gameweek_count = all_time_stats["counts"]["gameweek_participation"].get(manager, 0)
                    if gameweek_count > 0:
                        defensive_averages[manager] = all_time_stats["cumulative"]["defensive_points"][manager] / gameweek_count
                        attacking_averages[manager] = all_time_stats["cumulative"]["attacking_points"][manager] / gameweek_count

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

                if 'most_defensive_team' in locals():
                    output += f"### Most Defence-Heavy Team\n"
                    output += f"Team: {most_defensive_team[0]}\n"
                    output += f"Average Defensive Points (GK+DEF): {most_defensive_team[1]:.2f}\n\n"

                if 'most_attacking_team' in locals():
                    output += f"### Most Attack-Heavy Team\n"
                    output += f"Team: {most_attacking_team[0]}\n"
                    output += f"Average Attacking Points (MID+FWD): {most_attacking_team[1]:.2f}\n\n"
        except Exception as e:
            output += f"Error processing defensive/attacking balance data: {str(e)}\n\n"

        output_dir = f"{OUTPUT_BASE_DIR}/{league_name}"
        os.makedirs(output_dir, exist_ok=True)
        filepath = f"{output_dir}/{ALL_TIME_STATS_FILENAME}"
        with open(filepath, 'w') as file:
            file.write(output)
        print(f"All-time analysis saved to {filepath}")
    except Exception as e:
        raise ReportGenerationError(
            f"Error generating all-time analysis report for league {league_name}",
            report_type="all_time_analysis"
        ) from e