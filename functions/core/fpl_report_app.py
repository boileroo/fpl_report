from typing import Any, Dict, List
from functions.data.data_operations import fetch_raw_data, create_mappings
from functions.reporting.report_generation import generate_reports
from functions.processing.data_processing import process_gameweek_for_league, get_differential_king
from functions.core.all_time_stats import AllTimeStatsManager
from functions.exceptions import FPLReportError, APIClientError, DataFetchError
import os

class FPLReportApp:
    """Main application class that orchestrates the FPL report generation workflow"""
    
    def __init__(self) -> None:
        self.league_data: Dict[str, Any] = None
        self.player_data: Dict[int, Dict[str, Any]] = None
        self.all_time_stats_manager: AllTimeStatsManager = None
    
    def initialize_data(self, league_id: int, gameweek: int) -> bool:
        """Initialize data for a specific league and gameweek"""
        try:
            league_data_filepath, game_data_filepath = fetch_raw_data(league_id, gameweek)
            self.league_data, self.player_data = create_mappings(league_data_filepath, game_data_filepath)
            return True
        except DataFetchError as e:
            print(f"Error fetching data for league {league_id}: {e.message}")
            return False
        except Exception as e:
            print(f"Unexpected error while initializing data for league {league_id}: {str(e)}")
            return False
    
    def initialize_stats_manager(self, gameweek: int) -> bool:
        """Initialize the all-time stats manager"""
        try:
            league_name = self.league_data['name']
            self.all_time_stats_manager = AllTimeStatsManager(league_name, gameweek)
            return True
        except Exception as e:
            print(f"Error initializing stats manager: {str(e)}")
            return False
    
    def process_gameweek_data(self, gameweek: int) -> bool:
        """Process gameweek data for all teams in the league"""
        try:
            process_gameweek_for_league(
                self.league_data, 
                self.player_data, 
                gameweek, 
                self.all_time_stats_manager
            )
            return True
        except FPLReportError as e:
            print(f"Error processing gameweek data: {e.message}")
            return False
        except Exception as e:
            print(f"Unexpected error processing gameweek data: {str(e)}")
            return False
    
    def generate_reports(self, gameweek: int) -> bool:
        """Generate all reports for the current data"""
        try:
            generate_reports(
                self.league_data, 
                self.player_data, 
                gameweek, 
                self.all_time_stats_manager
            )
            return True
        except FPLReportError as e:
            print(f"Error generating reports: {e.message}")
            return False
        except Exception as e:
            print(f"Unexpected error generating reports: {str(e)}")
            return False
    
    def save_stats(self) -> bool:
        """Save the all-time stats"""
        try:
            self.all_time_stats_manager.save_stats()
            return True
        except Exception as e:
            print(f"Error saving stats: {str(e)}")
            return False
    
    def run_league_analysis(self, league_id: int, gameweek: int) -> bool:
        """Run complete analysis for a single league"""
        print(f"Processing league {league_id}, gameweek {gameweek}...")
        
        # Initialize data
        if not self.initialize_data(league_id, gameweek):
            print(f"Failed to initialize data for league {league_id}")
            return False
        
        # Initialize stats manager
        if not self.initialize_stats_manager(gameweek):
            print(f"Failed to initialize stats manager for league {league_id}")
            return False
        
        # Process gameweek data
        if not self.process_gameweek_data(gameweek):
            print(f"Failed to process gameweek data for league {league_id}")
            return False
        
        # Generate reports
        if not self.generate_reports(gameweek):
            print(f"Failed to generate reports for league {league_id}")
            return False
        
        # Save stats
        if not self.save_stats():
            print(f"Failed to save stats for league {league_id}")
            return False
        
        print(f"Successfully processed league {league_id}")
        return True