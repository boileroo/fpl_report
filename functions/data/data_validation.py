from typing import Any, Dict, List, Tuple, Union

def validate_league_data(league_data: Any) -> Tuple[bool, str]:
    """Validate league data structure"""
    if not league_data:
        return False, "League data is empty"
    
    if not isinstance(league_data, dict):
        return False, "League data should be a dictionary"
    
    if 'league' not in league_data:
        return False, "Missing 'league' in league data"
    
    if 'standings' not in league_data:
        return False, "Missing 'standings' in league data"
    
    if 'results' not in league_data['standings']:
        return False, "Missing 'results' in league standings"
    
    # Validate league name
    if 'name' not in league_data['league']:
        return False, "Missing 'name' in league info"
    
    # Validate standings results structure
    if not isinstance(league_data['standings']['results'], list):
        return False, "Standings results should be a list"
    
    return True, "Valid"

def validate_player_data(player_data: Any) -> Tuple[bool, str]:
    """Validate player data structure"""
    if not player_data:
        return False, "Player data is empty"
    
    # Check if it's a dict (processed data) or list (raw data)
    if isinstance(player_data, list):
        # Raw data from API - check that it's a list of dictionaries
        if len(player_data) == 0:
            return False, "Player data is empty"
        
        # Check a few sample entries to ensure structure
        sample_players = player_data[:3]  # Check first 3 entries
        for i, player in enumerate(sample_players):
            if not isinstance(player, dict):
                return False, f"Player entry {i} should be a dictionary"
            
            required_fields = ['id', 'web_name', 'event_points', 'element_type']
            for field in required_fields:
                if field not in player:
                    return False, f"Missing '{field}' in player entry {i}"
        
        return True, "Valid"
    
    elif isinstance(player_data, dict):
        # Processed data - check that it has the expected structure
        if len(player_data) == 0:
            return False, "Player data is empty"
        
        # Check a few sample entries to ensure structure
        sample_keys = list(player_data.keys())[:3]  # Check first 3 entries
        for key in sample_keys:
            player = player_data[key]
            if not isinstance(player, dict):
                return False, f"Player entry {key} should be a dictionary"
            
            required_fields = ['name', 'points', 'position']
            for field in required_fields:
                if field not in player:
                    return False, f"Missing '{field}' in player entry {key}"
        
        return True, "Valid"
    
    else:
        return False, "Player data should be a dictionary or list"

def validate_gameweek_data(gameweek_data: Any, gameweek: int) -> Tuple[bool, str]:
    """Validate gameweek data structure"""
    if not gameweek_data:
        return False, "Gameweek data is empty"
    
    if not isinstance(gameweek_data, dict):
        return False, "Gameweek data should be a dictionary"
    
    if str(gameweek) not in gameweek_data:
        return False, f"Missing gameweek {gameweek} in gameweek data"
    
    gw_data = gameweek_data[str(gameweek)]
    if not isinstance(gw_data, dict):
        return False, f"Gameweek {gameweek} data should be a dictionary"
    
    if 'picks' not in gw_data:
        return False, f"Missing 'picks' in gameweek {gameweek} data"
    
    # Validate picks structure
    picks = gw_data['picks']
    if not isinstance(picks, list):
        return False, f"Picks in gameweek {gameweek} should be a list"
    
    return True, "Valid"

def validate_team_data(team_data: Any, gameweek: int) -> Tuple[bool, str]:
    """Validate team data structure"""
    if not team_data:
        return False, "Team data is empty"
    
    if not isinstance(team_data, dict):
        return False, "Team data should be a dictionary"
    
    if 'gameweek_data' not in team_data:
        return False, "Missing 'gameweek_data' in team data"
    
    valid, message = validate_gameweek_data(team_data['gameweek_data'], gameweek)
    if not valid:
        return False, message
    
    return True, "Valid"

def validate_all_time_stats(stats: Any) -> Tuple[bool, str]:
    """Validate all-time stats structure"""
    if not stats:
        return False, "All-time stats data is empty"
    
    if not isinstance(stats, dict):
        return False, "All-time stats should be a dictionary"
    
    required_sections = ['records', 'cumulative', 'counts', 'manager_records', 'formations', 'gw_scores', 'differential_king_per_gameweek']
    for section in required_sections:
        if section not in stats:
            return False, f"Missing '{section}' section in all-time stats"
    
    return True, "Valid"

def validate_gameweek_picks(picks: Any) -> Tuple[bool, str]:
    """Validate individual gameweek picks structure"""
    if not isinstance(picks, list):
        return False, "Picks should be a list"
    
    if len(picks) == 0:
        return False, "Picks list is empty"
    
    # Check a few sample picks to ensure structure
    for i, pick in enumerate(picks[:3]):  # Check first 3 picks
        if not isinstance(pick, dict):
            return False, f"Pick {i} should be a dictionary"
        
        required_fields = ['element', 'position', 'is_captain', 'is_vice_captain', 'multiplier']
        for field in required_fields:
            if field not in pick:
                return False, f"Missing '{field}' in pick {i}"
    
    return True, "Valid"

def validate_entry_history(history: Any) -> Tuple[bool, str]:
    """Validate entry history structure (from team history API)"""
    if not history:
        return False, "Entry history is empty"
    
    if not isinstance(history, dict):
        return False, "Entry history should be a dictionary"
    
    if 'current' not in history:
        return False, "Missing 'current' in entry history"
    
    if not isinstance(history['current'], list):
        return False, "'current' in entry history should be a list"
    
    return True, "Valid"

def validate_gameweek_entry_history(entry_history: Any) -> Tuple[bool, str]:
    """Validate entry history structure (from gameweek picks API)"""
    if not entry_history:
        return False, "Gameweek entry history is empty"
    
    if not isinstance(entry_history, dict):
        return False, "Gameweek entry history should be a dictionary"
    
    # Check for required fields in gameweek entry history
    required_fields = ['points', 'rank', 'overall_rank', 'event_transfers', 'event_transfers_cost']
    for field in required_fields:
        if field not in entry_history:
            return False, f"Missing '{field}' in gameweek entry history"
    
    return True, "Valid"