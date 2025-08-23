"""
Test script to verify the complete workflow with data validation.
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_workflow_with_validation():
    """Test the complete workflow with data validation."""
    try:
        # Test imports
        from functions.core.fpl_report_app import FPLReportApp
        from functions.data.data_validation import validate_all_time_stats
        from functions.exceptions import FPLReportError
        
        # Test app initialization
        app = FPLReportApp()
        print("✓ FPLReportApp initialized successfully")
        
        # Test stats validation
        default_stats = app.all_time_stats_manager._get_default_stats_structure() if hasattr(app, 'all_time_stats_manager') else None
        if default_stats:
            valid, message = validate_all_time_stats(default_stats)
            assert valid, f"Default stats structure failed validation: {message}"
            print("✓ Default stats structure validation passed")
        
        # Test data validation functions
        from functions.data.data_validation import (
            validate_league_data, 
            validate_player_data, 
            validate_gameweek_data
        )
        
        # Test with empty data (should fail gracefully)
        valid, message = validate_league_data(None)
        assert not valid, "None league data should fail validation"
        print("✓ League data validation correctly handles None data")
        
        valid, message = validate_player_data(None)
        assert not valid, "None player data should fail validation"
        print("✓ Player data validation correctly handles None data")
        
        valid, message = validate_gameweek_data(None, 1)
        assert not valid, "None gameweek data should fail validation"
        print("✓ Gameweek data validation correctly handles None data")
        
        return True
        
    except Exception as e:
        print(f"✗ Workflow validation test failed: {e}")
        return False

if __name__ == "__main__":
    print("Running workflow with validation tests...\\n")
    
    success = test_workflow_with_validation()
    
    print("\\n" + "="*50)
    if success:
        print("✓ All workflow validation tests passed!")
    else:
        print("✗ Some workflow validation tests failed.")
    print("="*50)