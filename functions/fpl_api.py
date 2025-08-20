import requests

BASE_URL = "https://fantasy.premierleague.com/api/"

TEAM_ID_KEY = 'entry'

def _fetch_data(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch data from {url}.")
        return None
    return response.json()

def fetch_game_data():
    url = BASE_URL + "bootstrap-static/"
    return _fetch_data(url)

def fetch_league_data(league_id):
    url = BASE_URL + f"leagues-classic/{league_id}/standings/"
    return _fetch_data(url)

def fetch_team_data(team_id):
    url = BASE_URL + f"entry/{team_id}/"
    return _fetch_data(url)

def fetch_team_transfers(team_id):
    url = BASE_URL + f"entry/{team_id}/transfers/"
    return _fetch_data(url)

def fetch_team_history(team_id):
    url = BASE_URL + f"entry/{team_id}/history/"
    return _fetch_data(url)

def fetch_team_gameweek_data(team_id, gameweek):
    url = BASE_URL + f"entry/{team_id}/event/{gameweek}/picks/"
    return _fetch_data(url)

def retrieve_league_data(league_id, gameweek):
    league_data = fetch_league_data(league_id)
    
    if league_data is None:
        print(f"Error: Could not retrieve league data for ID {league_id}.")
        return None

    for entry in league_data.get('standings', {}).get('results', []):
        team_id = entry['entry']
        
        team_data = fetch_team_data(team_id)

        if team_data:
            entry['team_data'] = team_data
        else:
            print(f"Warning: Could not retrieve manager details for team {team_id}.")
            entry['team_data'] = {} # Initialize to avoid KeyErrors later

        transfers = fetch_team_transfers(team_id)
        if transfers:
            entry['transfers'] = transfers
        else:
            print(f"Warning: Could not retrieve transfers for team {team_id}.")
            entry['transfers'] = {}

        history = fetch_team_history(team_id)
        if history:
            entry['history'] = history
        else:
            print(f"Warning: Could not retrieve history for team {team_id}.")
            entry['history'] = {}
        
        entry['gameweek_data'] = {}
        gameweek_picks = fetch_team_gameweek_data(team_id, gameweek)
        if gameweek_picks:
            entry['gameweek_data'][gameweek] = gameweek_picks
        else:
            print(f"Warning: Could not retrieve gameweek {gameweek} data for team {team_id}.")
            entry['gameweek_data'][gameweek] = {}
    
    return league_data