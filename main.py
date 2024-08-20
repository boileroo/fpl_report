import json
import sys
import requests
import os
from datetime import datetime

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

def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def calculate_gw_average(mini_league_data, gw):
    total_points = sum(manager['history']['current'][gw - 1]['points'] for manager in mini_league_data['standings']['results'] if len(manager['history']['current']) > gw - 1)
    count = len(mini_league_data['standings']['results'])
    
    return total_points / count if count != 0 else 0

def get_detailed_gw_data(manager_data, desired_gw, player_id_to_name, player_id_to_points, player_id_to_position, mini_league_data):
    gw_data_list = []

    gw_data = manager_data['gameweek_data'].get(str(desired_gw), {})
    picks = gw_data.get('picks', [])
    entry_history = gw_data.get('entry_history', {})
    gw_data['points'] = entry_history.get('points', 0)
    gw_data['rank'] = entry_history.get('rank', 0)
    gw_data['event_transfers'] = entry_history.get('event_transfers', 0)
    gw_data['event_transfers_cost'] = entry_history.get('event_transfers_cost', 0)
    active_chip = gw_data.get('active_chip', "No Chip Used")

    top_scorer_id = max(picks, key=lambda x: player_id_to_points.get(x['element'], 0))['element']
    max_points = player_id_to_points.get(top_scorer_id, 0)
    top_scorer_position = next((pick['position'] for pick in picks if pick['element'] == top_scorer_id), None)
    top_scorer_played = top_scorer_position < 12 if top_scorer_position else False

    underperformer_id = min(picks, key=lambda x: player_id_to_points.get(x['element'], 0))['element']
    min_points = player_id_to_points.get(underperformer_id, 0)

    starting_players = [pick for pick in picks if pick['position'] <= 11]
    formation = "{}-{}-{}".format(
        sum(1 for pick in starting_players if player_id_to_position[pick['element']] == 2),
        sum(1 for pick in starting_players if player_id_to_position[pick['element']] == 3),
        sum(1 for pick in starting_players if player_id_to_position[pick['element']] == 4)
    )

    captain_id = next((pick['element'] for pick in picks if pick['is_captain']), None)
    captain_multiplier = next((pick['multiplier'] for pick in picks if pick['is_captain']), 1)
    vice_captain_id = next((pick['element'] for pick in picks if pick['is_vice_captain']), None)
    vice_captain_multiplier = next((pick['multiplier'] for pick in picks if pick['is_vice_captain']), 1)

    captain_name = player_id_to_name.get(captain_id, 'Unknown')
    captain_points = player_id_to_points.get(captain_id, 0) * captain_multiplier
    vice_captain_name = player_id_to_name.get(vice_captain_id, 'Unknown')
    vice_captain_points = player_id_to_points.get(vice_captain_id, 0) * vice_captain_multiplier

    defensive_points = sum(player_id_to_points[pick['element']] for pick in starting_players if player_id_to_position[pick['element']] in [1, 2])
    attacking_points = sum(player_id_to_points[pick['element']] for pick in starting_players if player_id_to_position[pick['element']] in [3, 4])

    chip_used = active_chip

    avg_points = calculate_gw_average(mini_league_data, desired_gw)
    gw_performance_vs_avg = gw_data['points'] - avg_points
    rank_movement = (manager_data.get('last_rank', 0) - manager_data.get('rank', 0))

    gw_data_list.append({
        'Gameweek': desired_gw,
        'Points': gw_data['points'],
        'Rank': gw_data['rank'],
        'Captain': captain_name,
        'Captain Points': captain_points,
        'Vice-Captain': vice_captain_name,
        'Vice-Captain Points': vice_captain_points,
        'Transfers': gw_data['event_transfers'],
        'Transfer Cost': gw_data['event_transfers_cost'],
        'Team Value': entry_history.get('value', 0) / 10,
        'Points on Bench': entry_history.get('points_on_bench', 0),
        'Bank Money': entry_history.get('bank', 0) / 10,
        'Top Scorer': player_id_to_name.get(top_scorer_id, 'Unknown'),
        'Top Scorer Points': max_points,
        'Top Scorer Played': top_scorer_played,
        'Underperformer': player_id_to_name.get(underperformer_id, 'Unknown'),
        'Underperformer Points': min_points,
        'Formation': formation,
        'Defensive Points': defensive_points,
        'Attacking Points': attacking_points,
        'Chip Used': chip_used,
        'Performance vs Avg': gw_performance_vs_avg,
        'Rank Movement': rank_movement
    })

    return gw_data_list

def main():
    gameweek = input("Please enter the current gameweek: ")
    league_id = input("Please enter the league id: ")
    
    os.makedirs("player_data", exist_ok=True)
    os.makedirs("league_data", exist_ok=True)

    mini_league_file = f"league_data/mini_league_data_gw{gameweek}.json"
    player_data_file = f"player_data/players_data_gw{gameweek}.json"

    # Always fetch new data
    mini_league_data = retrieve_mini_league_data(int(league_id), int(gameweek))
    save_to_json(mini_league_data, mini_league_file)

    player_data = fetch_bootstrap_data()
    save_to_json(player_data, player_data_file)
    
    print(f"Player data saved to {player_data_file}")
    print(f"Data saved to {mini_league_file}")

    # Load the newly fetched data
    with open(mini_league_file, 'r') as file:
        mini_league_data = json.load(file)

    with open(player_data_file, 'r') as file:
        players_data = json.load(file)['elements']

    player_id_to_name = {player['id']: player['web_name'] for player in players_data}
    player_id_to_points = {player['id']: player['event_points'] for player in players_data}
    player_id_to_position = {player['id']: player['element_type'] for player in players_data}

    output = f"Analysis generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # Extract detailed gameweek data for all managers in the mini-league
    for manager_data in mini_league_data['standings']['results']:
        manager_name = manager_data['entry_name']
        gw_data = get_detailed_gw_data(manager_data, int(gameweek), player_id_to_name, player_id_to_points, player_id_to_position, mini_league_data)

        output += f"\nManager: {manager_name}\n"
        output += "-" * 80 + "\n"
        for data in gw_data:
            output += f"Gameweek: {data['Gameweek']}\n"
            output += f"Points: {data['Points']}\n"
            output += f"Rank: {data['Rank']}\n"
            output += f"Captain: {data['Captain']}, {data['Captain Points']} points\n"
            output += f"Vice-Captain: {data['Vice-Captain']}, {data['Vice-Captain Points']} points\n"
            output += f"Transfers: {data['Transfers']}\n"
            output += f"Transfer Cost: {data['Transfer Cost']}\n"
            output += f"Team Value: {data['Team Value']}\n"
            output += f"Points on Bench: {data['Points on Bench']}\n"
            output += f"Bank Money: {data['Bank Money']}\n"
            output += f"Top Scorer: {data['Top Scorer']}, {data['Top Scorer Points']} points{' (on bench)' if not data['Top Scorer Played'] else ''}\n"
            output += f"Underperformer: {data['Underperformer']}, {data['Underperformer Points']} points\n"
            output += f"Formation: {data['Formation']}\n"
            output += f"Defensive Points: {data['Defensive Points']}\n"
            output += f"Attacking Points: {data['Attacking Points']}\n"
            output += f"Chip Used: {data['Chip Used']}\n"
            output += f"Performance vs Avg: {data['Performance vs Avg']}\n"
            output += f"Rank Movement: {data['Rank Movement']}\n"
            output += "-" * 80 + "\n"

    # Extract league standings
    league_standings = mini_league_data.get('standings', {}).get('results', [])
    team_data = [{'Team Name': team['entry_name'], 'Points': team['total']} for team in league_standings]

    output += "\nLeague Standings:\n"
    output += "Team Name,Points\n"
    for team in team_data:
        output += f"{team['Team Name']},{team['Points']}\n"

    # Save the output to a text file, overwriting any existing file
    with open(f"league_analysis_gw{gameweek}.txt", 'w') as file:
        file.write(output)

    print(output)
    print(f"Analysis saved to league_analysis_gw{gameweek}.txt")

if __name__ == "__main__":
    main()