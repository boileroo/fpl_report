import requests
from typing import Any, Dict, Optional, Union
from functions.exceptions import APIClientError
from functions.config import FPL_BASE_URL, FPL_TEAM_ID_KEY

TEAM_ID_KEY: str = FPL_TEAM_ID_KEY

def _fetch_data(url: str) -> Any:
    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            raise APIClientError(
                f"Failed to fetch data from {url}.",
                status_code=response.status_code,
                url=url
            )
        return response.json()
    except requests.exceptions.RequestException as e:
        raise APIClientError(
            f"Network error while fetching data from {url}: {str(e)}",
            url=url
        ) from e

def fetch_game_data() -> Dict[str, Any]:
    url = FPL_BASE_URL + "bootstrap-static/"
    return _fetch_data(url)

def fetch_league_data(league_id: int) -> Dict[str, Any]:
    url = FPL_BASE_URL + f"leagues-classic/{league_id}/standings/"
    return _fetch_data(url)

def fetch_team_data(team_id: int) -> Dict[str, Any]:
    url = FPL_BASE_URL + f"entry/{team_id}/"
    return _fetch_data(url)

def fetch_team_transfers(team_id: int) -> Dict[str, Any]:
    url = FPL_BASE_URL + f"entry/{team_id}/transfers/"
    return _fetch_data(url)

def fetch_team_history(team_id: int) -> Dict[str, Any]:
    url = FPL_BASE_URL + f"entry/{team_id}/history/"
    return _fetch_data(url)

def fetch_team_gameweek_data(team_id: int, gameweek: int) -> Dict[str, Any]:
    url = FPL_BASE_URL + f"entry/{team_id}/event/{gameweek}/picks/"
    return _fetch_data(url)

def retrieve_league_data(league_id: int, gameweek: int) -> Optional[Dict[str, Any]]:
    try:
        league_data = fetch_league_data(league_id)
    except APIClientError as e:
        raise APIClientError(
            f"Error: Could not retrieve league data for ID {league_id}.",
            url=e.url
        ) from e

    if not league_data or 'standings' not in league_data or 'results' not in league_data['standings']:
        raise APIClientError(
            f"Invalid league data structure received for ID {league_id}.",
            url=FPL_BASE_URL + f"leagues-classic/{league_id}/standings/"
        )

    for entry in league_data['standings']['results']:
        team_id = entry['entry']
        
        try:
            team_data = fetch_team_data(team_id)
            if team_data:
                entry['team_data'] = team_data
            else:
                entry['team_data'] = {}
        except APIClientError:
            entry['team_data'] = {}

        try:
            transfers = fetch_team_transfers(team_id)
            entry['transfers'] = transfers or {}
        except APIClientError:
            entry['transfers'] = {}

        try:
            history = fetch_team_history(team_id)
            entry['history'] = history or {}
        except APIClientError:
            entry['history'] = {}
        
        entry['gameweek_data'] = {}
        try:
            gameweek_picks = fetch_team_gameweek_data(team_id, gameweek)
            entry['gameweek_data'][gameweek] = gameweek_picks or {}
        except APIClientError:
            entry['gameweek_data'][gameweek] = {}
    
    return league_data