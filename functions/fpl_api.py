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
    bootstrap_data = fetch_bootstrap_data()
    
    league_data = fetch_league_data(league_id)
    
    for entry in league_data['standings']['results']:
        team_id = entry['entry']
        
        entry['manager_details'] = fetch_manager_data(team_id)
        entry['transfers'] = fetch_manager_transfers(team_id)
        entry['history'] = fetch_manager_history(team_id)
        
        entry['gameweek_data'] = {}
        gw = str(gameweek)
        entry['gameweek_data'][gw] = fetch_gameweek_data_for_team(team_id, gw)
    
    return league_data