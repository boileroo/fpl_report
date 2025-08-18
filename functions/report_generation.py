from datetime import datetime
from functions.data_processing import get_detailed_gw_data

def generate_analysis_report(gameweek, mini_league_data, player_id_to_name, player_id_to_points, player_id_to_position):
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