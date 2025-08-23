"""
Test script to verify the refactored FPL report application structure.
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """Test that all modules can be imported successfully."""
    try:
        # Test main application
        from functions.core.fpl_report_app import FPLReportApp
        print("✓ FPLReportApp imported successfully")
        
        # Test exceptions
        from functions.exceptions import FPLReportError, APIClientError, DataFetchError
        print("✓ Exception classes imported successfully")
        
        # Test configuration
        from functions.config import FPL_BASE_URL, OUTPUT_BASE_DIR
        print("✓ Configuration imported successfully")
        
        # Test data utilities
        from functions.data.data_utils import safe_get_nested_value, safe_divide
        print("✓ Data utilities imported successfully")
        
        # Test core modules
        from functions.api.fpl_api import fetch_game_data
        from functions.data.data_operations import fetch_raw_data
        from functions.processing.data_processing import get_detailed_gw_data
        from functions.core.all_time_stats import AllTimeStatsManager
        from functions.reporting.report_generation import generate_reports
        
        print("✓ Core modules imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Import test failed: {e}")
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
    print("Running FPL Report structure tests...\\n")
    
    success = True
    success &= test_imports()
    print()
    success &= test_app_initialization()
    
    print("\\n" + "="*50)
    if success:
        print("✓ All tests passed! The refactored structure is working correctly.")
    else:
        print("✗ Some tests failed. Please check the errors above.")
    print("="*50)