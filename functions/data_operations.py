import os
import sys # Added for sys.exit()
from functions.fpl_api import retrieve_league_data, fetch_bootstrap_data
from functions.file_operations import save_to_json, load_json

def get_formatted_league_name(league_data):
    return league_data['league']['name'].replace(" ", "_").replace("/", "_").lower()

def fetch_and_save_raw_data(gameweek, league_id):
    league_data = retrieve_league_data(int(league_id), int(gameweek))
    if league_data is None:
        print("Error: Could not retrieve mini-league data.")
        import sys
        sys.exit(1)

    league_name = get_formatted_league_name(league_data)
    
    output_dir = f"outputs/{league_name}/gameweek_{gameweek}"
    os.makedirs(output_dir, exist_ok=True)

    league_filepath = f"{output_dir}/league_data.json"
    player_data_filepath = f"{output_dir}/players_data.json"

    save_to_json(league_data, league_filepath)

    player_data = fetch_bootstrap_data()
    if player_data is None:
        print("Error: Could not retrieve player bootstrap data.")
        import sys
        sys.exit(1)
        
    save_to_json(player_data, player_data_filepath)
    
    print(f"Player data saved to {player_data_filepath}")
    print(f"Data saved to {league_filepath}")
    return league_filepath, player_data_filepath

def load_data_and_create_mappings(league_filepath, player_data_filepath):
    league_data = load_json(league_filepath)
    players_data = load_json(player_data_filepath)['elements']

    player_id_to_name = {player['id']: player['web_name'] for player in players_data}
    player_id_to_points = {player['id']: player['event_points'] for player in players_data}
    player_id_to_position = {player['id']: player['element_type'] for player in players_data}
    
    return league_data, player_id_to_name, player_id_to_points, player_id_to_position