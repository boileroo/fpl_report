"""
Test script to verify the type hints work correctly.
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_type_hints():
    """Test that all modules with type hints can be imported successfully."""
    try:
        # Test main application
        from functions.core.fpl_report_app import FPLReportApp
        print("✓ FPLReportApp imported successfully")
        
        # Test exceptions with type hints
        from functions.exceptions import FPLReportError, APIClientError, DataFetchError
        print("✓ Exception classes imported successfully")
        
        # Test configuration with type hints
        from functions.config import FPL_BASE_URL, OUTPUT_BASE_DIR
        print("✓ Configuration imported successfully")
        
        # Test data utilities with type hints
        from functions.data.data_utils import safe_get_nested_value, safe_divide
        print("✓ Data utilities imported successfully")
        
        # Test data validation with type hints
        from functions.data.data_validation import validate_league_data, validate_player_data
        print("✓ Data validation imported successfully")
        
        # Test core modules with type hints
        from functions.api.fpl_api import fetch_game_data
        from functions.data.data_operations import fetch_raw_data
        from functions.processing.data_processing import get_detailed_gw_data
        from functions.core.all_time_stats import AllTimeStatsManager
        from functions.reporting.report_generation import generate_reports
        from functions.utils import get_formatted_league_name, save_to_json, load_json
        
        print("✓ Core modules with type hints imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Type hints test failed: {e}")
        return False

def test_app_initialization():
    """Test that the main application can be initialized."""
    try:
        from functions.core.fpl_report_app import FPLReportApp
        app = FPLReportApp()
        print("✓ FPLReportApp initialized successfully")
        return True
    except Exception as e:
        print(f"✗ App initialization failed: {e}")
        return False

if __name__ == "__main__":
    print("Running type hints tests...\n")
    
    success = True
    success &= test_type_hints()
    print()
    success &= test_app_initialization()
    
    print("\n" + "="*50)
    if success:
        print("✓ All type hints tests passed!")
    else:
        print("✗ Some type hints tests failed.")
    print("="*50)