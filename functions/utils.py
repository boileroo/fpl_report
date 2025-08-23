import json

def get_formatted_league_name(league_data):
    return league_data['league']['name'].replace(" ", "_").replace("/", "_").lower()

def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def ensure_directory_exists(filepath):
    filepath.parent.mkdir(parents=True, exist_ok=True)
