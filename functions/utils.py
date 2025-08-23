import json
from pathlib import Path
from typing import Any, Dict, Union

def get_formatted_league_name(league_data: Dict[str, Any]) -> str:
    return league_data['league']['name'].replace(" ", "_").replace("/", "_").lower()

def save_to_json(data: Any, filename: Union[str, Path]) -> None:
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def load_json(filename: Union[str, Path]) -> Any:
    with open(filename, 'r') as f:
        return json.load(f)

def ensure_directory_exists(filepath: Union[str, Path]) -> None:
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
