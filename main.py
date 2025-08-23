import warnings
from typing import List, Tuple
from functions.core.fpl_report_app import FPLReportApp
import sys

# Suppress urllib3 OpenSSL compatibility warning on macOS
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL 1.1.1+")

def _parse_arguments() -> Tuple[int, List[int]]:
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <gameweek> [league_id1] [league_id2] ...")
        sys.exit(1)
    
    try:
        gameweek = int(sys.argv[1])
    except ValueError:
        print(f"Error: Gameweek must be a number, got '{sys.argv[1]}'")
        sys.exit(1)
    
    # If no league IDs provided, use fallback
    if len(sys.argv) == 2:
        league_ids = [1523783, 952600]
    else:
        try:
            league_ids = [int(arg) for arg in sys.argv[2:]]
        except ValueError as e:
            print(f"Error: League IDs must be numbers. Invalid value: {e}")
            sys.exit(1)

    return gameweek, league_ids

def main() -> None:
    gameweek, league_ids = _parse_arguments()
    
    app = FPLReportApp()
    
    for league_id in league_ids:
        success = app.run_league_analysis(league_id, gameweek)
        if not success:
            print(f"Failed to process league {league_id}")
            continue

if __name__ == "__main__":
    main()