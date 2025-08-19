def calculate_gw_average(league_data, gw):
    total_points = sum(manager['history']['current'][gw - 1]['points'] for manager in league_data['standings']['results'] if len(manager['history']['current']) > gw - 1)
    count = len(league_data['standings']['results'])
    
    return total_points / count if count != 0 else 0

def get_detailed_gw_data(manager_data, desired_gw, player_id_to_name, player_id_to_points, player_id_to_position, league_data):
    gw_data_list = []

    gw_data = manager_data['gameweek_data'].get(str(desired_gw), {})
    picks = gw_data.get('picks', [])
    if not picks: # If no picks data, return empty list
        return []

    entry_history = gw_data.get('entry_history', {})
    gw_data['points'] = entry_history.get('points', 0)
    gw_data['overall_gameweek_rank'] = entry_history.get('rank', 0)
    gw_data['overall_rank'] = entry_history.get('overall_rank', 0)
    gw_data['league_rank'] = manager_data.get('rank_sort', 0)
    gw_data['event_transfers'] = entry_history.get('event_transfers', 0)
    gw_data['event_transfers_cost'] = entry_history.get('event_transfers_cost', 0)
    active_chip = gw_data.get('active_chip', "No Chip Used")

    # Safely get max/min when picks might be empty or points are uniform
    top_scorer_id = None
    max_points = 0
    underperformer_id = None
    min_points = 0
    
    if picks:
        top_scorer_pick = max(picks, key=lambda x: player_id_to_points.get(x['element'], 0))
        top_scorer_id = top_scorer_pick['element']
        max_points = player_id_to_points.get(top_scorer_id, 0)

        underperformer_pick = min(picks, key=lambda x: player_id_to_points.get(x['element'], 0))
        underperformer_id = underperformer_pick['element']
        min_points = player_id_to_points.get(underperformer_id, 0)

    top_scorer_position = next((pick['position'] for pick in picks if pick['element'] == top_scorer_id), None)
    top_scorer_played = top_scorer_position < 12 if top_scorer_position else False

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

    avg_points = calculate_gw_average(league_data, desired_gw)
    gw_performance_vs_avg = round(gw_data['points'] - avg_points, 1)
    league_rank_movement = (manager_data.get('last_rank', 0) - manager_data.get('rank', 0))

    gw_data_list.append({
        'Gameweek': desired_gw,
        'Points': gw_data['points'],
        'Overall Gameweek Rank': gw_data['overall_gameweek_rank'],
        'Overall Rank': gw_data['overall_rank'],
        'League Rank': gw_data['league_rank'],
        'League Rank Movement': league_rank_movement,
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
        'Performance vs Avg': gw_performance_vs_avg
    })

    return gw_data_list

def get_differential_king_queen(league_data, desired_gw, player_id_to_name, player_id_to_points):
    player_ownership = {} # player_id: [list of manager_names who own this player]

    # Iterate through all managers to build player ownership data
    for manager_data in league_data['standings']['results']:
        manager_name = manager_data['entry_name']
        gw_picks = manager_data['gameweek_data'].get(str(desired_gw), {}).get('picks', [])
        for pick in gw_picks:
            player_id = pick['element']
            if player_id not in player_ownership:
                player_ownership[player_id] = []
            player_ownership[player_id].append(manager_name)

    differential_players = []
    for player_id, owners in player_ownership.items():
        if len(owners) == 1: # Owned by only one manager
            player_name = player_id_to_name.get(player_id, 'Unknown Player')
            player_points = player_id_to_points.get(player_id, 0)
            differential_players.append({
                'player_id': player_id,
                'player_name': player_name,
                'points': player_points,
                'owner': owners[0] # The single owner
            })

    # Find the differential player with the highest score
    if differential_players:
        differential_king_queen = max(differential_players, key=lambda x: x['points'])
        return differential_king_queen
    else:
        return None # No differential player found
