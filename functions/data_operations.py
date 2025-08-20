import os
import sys # Added for sys.exit()
from functions.fpl_api import retrieve_league_data, fetch_game_data
from functions.file_operations import save_to_json, load_json
from functions.utils import get_formatted_league_name


def fetch_raw_data( league_id, gameweek):
    league_data = retrieve_league_data(league_id, gameweek)
    if league_data is None:
        print("Error: Could not retrieve mini-league data.")
        import sys
        sys.exit(1)

    league_name = get_formatted_league_name(league_data)
    
    output_dir = f"outputs/{league_name}/gameweek_{gameweek}"
    os.makedirs(output_dir, exist_ok=True)

    league_filepath = f"{output_dir}/league_data.json"
    game_data_filepath = f"{output_dir}/game_data.json"

    save_to_json(league_data, league_filepath)

    game_data = fetch_game_data()
    
    if game_data is None:
        print("Error: Could not retrieve game data.")
        import sys
        sys.exit(1)
        
    save_to_json(game_data, game_data_filepath)
    
    return league_filepath, game_data_filepath

def create_mappings(league_filepath, player_data_filepath):
    raw_players_data = load_json(player_data_filepath)['elements']
    league_data = load_json(league_filepath)
    
    league_data['name'] = get_formatted_league_name(league_data)

    player_data = {
        player['id']: {
            'name': player['web_name'],
            'points': player['event_points'],
            'position': player['element_type']
        }
        for player in raw_players_data
    }
    
    return league_data, player_data