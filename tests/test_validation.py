"""
Test script to verify data validation functions work correctly with various inputs.
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_validation_functions():
    """Test the data validation functions."""
    try:
        from functions.data.data_validation import (
            validate_league_data, 
            validate_player_data, 
            validate_gameweek_data,
            validate_team_data,
            validate_all_time_stats
        )
        
        # Test valid league data
        valid_league_data = {
            'league': {'name': 'Test League'},
            'standings': {
                'results': [
                    {'entry_name': 'Team 1', 'total': 100},
                    {'entry_name': 'Team 2', 'total': 90}
                ]
            }
        }
        
        valid, message = validate_league_data(valid_league_data)
        assert valid, f"Valid league data failed validation: {message}"
        print("✓ League data validation passed for valid data")
        
        # Test invalid league data
        invalid_league_data = {'standings': {}}
        valid, message = validate_league_data(invalid_league_data)
        assert not valid, "Invalid league data should fail validation"
        print("✓ League data validation correctly failed for invalid data")
        
        # Test valid player data
        valid_player_data = {
            1: {'name': 'Player 1', 'points': 10, 'position': 1},
            2: {'name': 'Player 2', 'points': 8, 'position': 2}
        }
        
        valid, message = validate_player_data(valid_player_data)
        assert valid, f"Valid player data failed validation: {message}"
        print("✓ Player data validation passed for valid data")
        
        # Test invalid player data
        invalid_player_data = "not a dict"
        valid, message = validate_player_data(invalid_player_data)
        assert not valid, "Invalid player data should fail validation"
        print("✓ Player data validation correctly failed for invalid data")
        
        # Test valid gameweek data
        valid_gw_data = {
            '1': {
                'picks': [
                    {'element': 1, 'position': 1, 'is_captain': True, 'is_vice_captain': False, 'multiplier': 2}
                ]
            }
        }
        
        valid, message = validate_gameweek_data(valid_gw_data, 1)
        assert valid, f"Valid gameweek data failed validation: {message}"
        print("✓ Gameweek data validation passed for valid data")
        
        # Test valid all-time stats
        valid_stats = {
            'records': {},
            'cumulative': {},
            'counts': {},
            'manager_records': {},
            'formations': {},
            'gw_scores': {},
            'differential_king_per_gameweek': {}
        }
        
        valid, message = validate_all_time_stats(valid_stats)
        assert valid, f"Valid all-time stats failed validation: {message}"
        print("✓ All-time stats validation passed for valid data")
        
        return True
        
    except Exception as e:
        print(f"✗ Data validation test failed: {e}")
        return False

if __name__ == "__main__":
    print("Running data validation tests...\n")
    
    success = test_validation_functions()
    
    print("\n" + "="*50)
    if success:
        print("✓ All data validation tests passed!")
    else:
        print("✗ Some data validation tests failed.")
    print("="*50)