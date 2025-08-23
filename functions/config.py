from typing import Dict, List

# FPL API Configuration
FPL_BASE_URL: str = "https://fantasy.premierleague.com/api/"
FPL_TEAM_ID_KEY: str = 'entry'

# File Paths
OUTPUT_BASE_DIR: str = "outputs"
LEAGUE_DATA_FILENAME: str = "league_data.json"
GAME_DATA_FILENAME: str = "game_data.json"
GW_ANALYSIS_FILENAME: str = "gw_analysis.txt"
ALL_TIME_STATS_FILENAME: str = "all_time_analysis.md"
ALL_TIME_STATS_GW_FILENAME_TEMPLATE: str = "all_time_stats_gw_{}.json"

# Default League IDs
DEFAULT_LEAGUE_IDS: List[int] = [1523783, 952600]

# Player Position Mappings
PLAYER_POSITIONS: Dict[int, str] = {
    1: "GK",
    2: "DEF",
    3: "MID", 
    4: "FWD"
}

# Chip Names
CHIP_NAMES: Dict[str, str] = {
    "BB": "Bench Boost",
    "TC": "Triple Captain",
    "FH": "Free Hit",
    "WC": "Wildcard"
}

# Formation Calculation
FORMATION_POSITIONS: Dict[int, str] = {
    2: "DEF",
    3: "MID", 
    4: "FWD"
}