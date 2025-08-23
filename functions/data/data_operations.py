import os
from typing import Any, Dict, Tuple
from functions.api.fpl_api import retrieve_league_data, fetch_game_data
from functions.utils import save_to_json, load_json
from functions.utils import get_formatted_league_name
from functions.exceptions import DataFetchError
from functions.config import OUTPUT_BASE_DIR, LEAGUE_DATA_FILENAME, GAME_DATA_FILENAME
from functions.data.data_validation import validate_league_data, validate_player_data


def fetch_raw_data(league_id: int, gameweek: int) -> Tuple[str, str]:
    try:
        league_data = retrieve_league_data(league_id, gameweek)
    except Exception as e:
        raise DataFetchError(
            f"Error: Could not retrieve mini-league data for league ID {league_id}.",
            source="league_data"
        ) from e

    if league_data is None:
        raise DataFetchError(
            f"Error: Could not retrieve mini-league data for league ID {league_id}.",
            source="league_data"
        )
    
    # Validate league data
    valid, message = validate_league_data(league_data)
    if not valid:
        raise DataFetchError(
            f"Invalid league data structure for league ID {league_id}: {message}",
            source="league_data_validation"
        )

    try:
        league_name = get_formatted_league_name(league_data)
    except Exception as e:
        raise DataFetchError(
            "Error: Could not format league name.",
            source="league_name"
        ) from e
    
    output_dir = f"{OUTPUT_BASE_DIR}/{league_name}/gameweek_{gameweek}"
    os.makedirs(output_dir, exist_ok=True)

    league_filepath = f"{output_dir}/{LEAGUE_DATA_FILENAME}"
    game_data_filepath = f"{output_dir}/{GAME_DATA_FILENAME}"

    try:
        save_to_json(league_data, league_filepath)
    except Exception as e:
        raise DataFetchError(
            f"Error: Could not save league data to {league_filepath}.",
            source="save_league_data"
        ) from e

    try:
        game_data = fetch_game_data()
    except Exception as e:
        raise DataFetchError(
            "Error: Could not retrieve game data.",
            source="game_data"
        ) from e
    
    if game_data is None:
        raise DataFetchError(
            "Error: Could not retrieve game data.",
            source="game_data"
        )
        
    try:
        save_to_json(game_data, game_data_filepath)
    except Exception as e:
        raise DataFetchError(
            f"Error: Could not save game data to {game_data_filepath}.",
            source="save_game_data"
        ) from e
    
    return league_filepath, game_data_filepath

def create_mappings(league_filepath: str, player_data_filepath: str) -> Tuple[Dict[str, Any], Dict[int, Dict[str, Any]]]:
    try:
        raw_game_data = load_json(player_data_filepath)
        raw_players_data = raw_game_data['elements']
        league_data = load_json(league_filepath)
    except Exception as e:
        raise DataFetchError(
            "Error: Could not load required data files.",
            source="load_data_files"
        ) from e
    
    try:
        league_data['name'] = get_formatted_league_name(league_data)
    except Exception as e:
        raise DataFetchError(
            "Error: Could not format league name.",
            source="format_league_name"
        ) from e

    # Validate raw player data
    valid, message = validate_player_data(raw_players_data)
    if not valid:
        raise DataFetchError(
            f"Invalid player data structure: {message}",
            source="player_data_validation"
        )

    try:
        player_data = {
            player['id']: {
                'name': player['web_name'],
                'points': player['event_points'],
                'position': player['element_type']
            }
            for player in raw_players_data
        }
    except Exception as e:
        raise DataFetchError(
            "Error: Could not create player data mappings.",
            source="create_mappings"
        ) from e
    
    return league_data, player_data