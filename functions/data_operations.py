import os
from functions.fpl_api import retrieve_mini_league_data, fetch_bootstrap_data
from functions.file_operations import save_to_json, load_json

def get_formatted_league_name(mini_league_data):
    return mini_league_data['league']['name'].replace(" ", "_").replace("/", "_").lower()

def fetch_and_save_raw_data(gameweek, league_id):
    mini_league_data = retrieve_mini_league_data(int(league_id), int(gameweek))
    league_name = get_formatted_league_name(mini_league_data)
    
    output_dir = f"outputs/{league_name}/gameweek_{gameweek}"
    os.makedirs(output_dir, exist_ok=True)

    mini_league_file = f"{output_dir}/mini_league_data.json"
    player_data_file = f"{output_dir}/players_data.json"

    save_to_json(mini_league_data, mini_league_file)

    player_data = fetch_bootstrap_data()
    save_to_json(player_data, player_data_file)
    
    print(f"Player data saved to {player_data_file}")
    print(f"Data saved to {mini_league_file}")
    return mini_league_file, player_data_file

def load_data_and_create_mappings(mini_league_file, player_data_file):
    mini_league_data = load_json(mini_league_file)
    players_data = load_json(player_data_file)['elements']

    player_id_to_name = {player['id']: player['web_name'] for player in players_data}
    player_id_to_points = {player['id']: player['event_points'] for player in players_data}
    player_id_to_position = {player['id']: player['element_type'] for player in players_data}
    
    return mini_league_data, player_id_to_name, player_id_to_points, player_id_to_position