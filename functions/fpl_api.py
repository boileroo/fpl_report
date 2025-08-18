import requests

BASE_URL = "https://fantasy.premierleague.com/api/"

def fetch_data(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch data from {url}.")
        return None
    return response.json()

def fetch_bootstrap_data():
    url = BASE_URL + "bootstrap-static/"
    return fetch_data(url)

def fetch_league_data(league_id):
    url = BASE_URL + f"leagues-classic/{league_id}/standings/"
    return fetch_data(url)

def fetch_manager_data(team_id):
    url = BASE_URL + f"entry/{team_id}/"
    return fetch_data(url)

def fetch_manager_transfers(team_id):
    url = BASE_URL + f"entry/{team_id}/transfers/"
    return fetch_data(url)

def fetch_manager_history(team_id):
    url = BASE_URL + f"entry/{team_id}/history/"
    return fetch_data(url)

def fetch_gameweek_data_for_team(team_id, gameweek):
    url = BASE_URL + f"entry/{team_id}/event/{gameweek}/picks/"
    return fetch_data(url)

def retrieve_mini_league_data(league_id, gameweek):
    league_data = fetch_league_data(league_id)
    
    if league_data is None:
        print(f"Error: Could not retrieve league data for ID {league_id}.")
        return None

    for entry in league_data.get('standings', {}).get('results', []):
        team_id = entry['entry']
        
        manager_details = fetch_manager_data(team_id)
        if manager_details:
            entry['manager_details'] = manager_details
        else:
            print(f"Warning: Could not retrieve manager details for team {team_id}.")
            entry['manager_details'] = {} # Initialize to avoid KeyErrors later

        transfers = fetch_manager_transfers(team_id)
        if transfers:
            entry['transfers'] = transfers
        else:
            print(f"Warning: Could not retrieve transfers for team {team_id}.")
            entry['transfers'] = {}

        history = fetch_manager_history(team_id)
        if history:
            entry['history'] = history
        else:
            print(f"Warning: Could not retrieve history for team {team_id}.")
            entry['history'] = {}
        
        entry['gameweek_data'] = {}
        gw = str(gameweek)
        gameweek_picks = fetch_gameweek_data_for_team(team_id, gw)
        if gameweek_picks:
            entry['gameweek_data'][gw] = gameweek_picks
        else:
            print(f"Warning: Could not retrieve gameweek {gw} data for team {team_id}.")
            entry['gameweek_data'][gw] = {}
    
    return league_data