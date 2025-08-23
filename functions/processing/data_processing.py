from typing import Any, Dict, List, Optional, Tuple, Union
from functions.exceptions import DataProcessingError
from functions.data.data_utils import safe_get_nested_value, safe_divide
from functions.data.data_validation import validate_team_data, validate_gameweek_picks, validate_entry_history, validate_gameweek_entry_history
import statistics

def calculate_gw_average(league_data: Dict[str, Any], gameweek: int) -> float:
    try:
        total_points = 0
        valid_managers = 0
        
        for manager in league_data['standings']['results']:
            # Check if manager has history data and enough gameweeks
            if ('history' in manager and 
                'current' in manager['history'] and 
                len(manager['history']['current']) >= gameweek):
                try:
                    points = manager['history']['current'][gameweek - 1]['points']
                    total_points += points
                    valid_managers += 1
                except (IndexError, KeyError):
                    # Skip managers without data for this gameweek
                    continue
        
        return safe_divide(total_points, valid_managers)
    except Exception as e:
        raise DataProcessingError(
            f"Error calculating gameweek average for gameweek {gameweek}",
            context="calculate_gw_average"
        ) from e

def get_detailed_gw_data(league_data: Dict[str, Any], team_data: Dict[str, Any], player_data: Dict[int, Dict[str, Any]], gameweek: int) -> List[Dict[str, Any]]:
    try:
        # Validate team data structure
        valid, message = validate_team_data(team_data, gameweek)
        if not valid:
            raise DataProcessingError(
                f"Invalid team data structure: {message}",
                context="team_data_validation"
            )

        team_gameweek_data_list: List[Dict[str, Any]] = []

        team_data_for_gameweek = team_data['gameweek_data'].get(str(gameweek), {})
        players = team_data_for_gameweek.get('picks', [])
        
        # Validate picks structure
        if players:
            valid, message = validate_gameweek_picks(players)
            if not valid:
                print(f"Warning: Invalid picks structure for team: {message}")
                return []

        if not players: 
            return []
        
        entry_history = team_data_for_gameweek.get('entry_history', {})
        
        # Validate entry history
        if entry_history:
            valid, message = validate_gameweek_entry_history(entry_history)
            if not valid:
                print(f"Warning: Invalid entry history structure: {message}")
        
        team_data_for_gameweek['points'] = entry_history.get('points', 0)
        team_data_for_gameweek['overall_gameweek_rank'] = entry_history.get('rank', 0)
        team_data_for_gameweek['overall_rank'] = entry_history.get('overall_rank', 0)
        team_data_for_gameweek['league_rank'] = team_data.get('rank_sort', 0)
        team_data_for_gameweek['event_transfers'] = entry_history.get('event_transfers', 0)
        team_data_for_gameweek['event_transfers_cost'] = entry_history.get('event_transfers_cost', 0)
        active_chip = team_data_for_gameweek.get('active_chip', "No Chip Used")
        
        automatic_subs = team_data_for_gameweek.get('automatic_subs', [])
        current_gw_autosubs = [
            sub for sub in automatic_subs
            if sub.get('event') == gameweek
        ]
        
        autosub_details: List[Dict[str, Any]] = []
        autosub_points = 0
        
        for autosub in current_gw_autosubs:
            element_in = autosub.get('element_in')
            element_out = autosub.get('element_out')
            
            if element_in is None or element_out is None:
                continue
                
            player_in_data = player_data.get(element_in, {})
            player_out_data = player_data.get(element_out, {})
            
            points_gained = player_in_data.get('points', 0)
            autosub_points += points_gained
            
            autosub_details.append({
                'element_in': element_in,
                'element_out': element_out,
                'player_in_name': player_in_data.get('name', 'Unknown'),
                'player_out_name': player_out_data.get('name', 'Unknown'),
                'points_gained': points_gained
            })

        # Handle case where there are no players
        if not players:
            top_scorer_id = None
            max_points = 0
            underperformer_id = None
            min_points = 0
        else:
            try:
                top_scorer_pick = max(players, key=lambda x: player_data.get(x['element'], {}).get('points', 0))
                top_scorer_id = top_scorer_pick['element']
                max_points = player_data.get(top_scorer_id, {}).get('points', 0)

                underperformer_pick = min(players, key=lambda x: player_data.get(x['element'], {}).get('points', 0))
                underperformer_id = underperformer_pick['element']
                min_points = player_data.get(underperformer_id, {}).get('points', 0)
            except ValueError:
                # Handle case where max/min on empty sequence
                top_scorer_id = None
                max_points = 0
                underperformer_id = None
                min_points = 0

        top_scorer_position = next((pick['position'] for pick in players if pick['element'] == top_scorer_id), None) if top_scorer_id else None
        top_scorer_played = top_scorer_position < 12 if top_scorer_position else False

        starting_players = [pick for pick in players if pick['position'] <= 11]
        
        # Calculate formation safely
        try:
            defenders = sum(1 for pick in starting_players if player_data.get(pick['element'], {}).get('position') == 2)
            midfielders = sum(1 for pick in starting_players if player_data.get(pick['element'], {}).get('position') == 3)
            forwards = sum(1 for pick in starting_players if player_data.get(pick['element'], {}).get('position') == 4)
            formation = "{}-{}-{}".format(defenders, midfielders, forwards)
        except Exception:
            formation = "Unknown"

        captain_id = next((pick['element'] for pick in players if pick['is_captain']), None)
        captain_multiplier = next((pick['multiplier'] for pick in players if pick['is_captain']), 1)
        vice_captain_id = next((pick['element'] for pick in players if pick['is_vice_captain']), None)
        vice_captain_multiplier = next((pick['multiplier'] for pick in players if pick['is_vice_captain']), 1)

        captain_name = player_data.get(captain_id, {}).get('name', 'Unknown') if captain_id else 'Unknown'
        captain_points = (player_data.get(captain_id, {}).get('points', 0) * captain_multiplier) if captain_id else 0
        vice_captain_name = player_data.get(vice_captain_id, {}).get('name', 'Unknown') if vice_captain_id else 'Unknown'
        vice_captain_points = (player_data.get(vice_captain_id, {}).get('points', 0) * vice_captain_multiplier) if vice_captain_id else 0

        defensive_points = sum(player_data.get(pick['element'], {}).get('points', 0) for pick in starting_players if player_data.get(pick['element'], {}).get('position') in [1, 2])
        attacking_points = sum(player_data.get(pick['element'], {}).get('points', 0) for pick in starting_players if player_data.get(pick['element'], {}).get('position') in [3, 4])

        chip_used = active_chip

        try:
            avg_points = calculate_gw_average(league_data, gameweek)
            gw_performance_vs_avg = round(team_data_for_gameweek['points'] - avg_points, 1)
        except Exception:
            gw_performance_vs_avg = 0

        if gameweek == 1:
            league_rank_movement = 0
        else:
            league_rank_movement = (team_data.get('last_rank', 0) - team_data.get('rank', 0))

        team_gameweek_data_list.append({
            'Gameweek': gameweek,
            'Points': team_data_for_gameweek['points'],
            'Overall Gameweek Rank': team_data_for_gameweek['overall_gameweek_rank'],
            'Overall Rank': team_data_for_gameweek['overall_rank'],
            'League Rank': team_data_for_gameweek['league_rank'],
            'League Rank Movement': league_rank_movement,
            'Captain': captain_name,
            'Captain Points': captain_points,
            'Vice-Captain': vice_captain_name,
            'Vice-Captain Points': vice_captain_points,
            'Transfers': team_data_for_gameweek['event_transfers'],
            'Transfer Cost': team_data_for_gameweek['event_transfers_cost'],
            'Team Value': entry_history.get('value', 0) / 10,
            'Points on Bench': entry_history.get('points_on_bench', 0),
            'Bank Money': entry_history.get('bank', 0) / 10,
            'Top Scorer': player_data.get(top_scorer_id, {}).get('name', 'Unknown') if top_scorer_id else 'Unknown',
            'Top Scorer Points': max_points,
            'Top Scorer Played': top_scorer_played,
            'Underperformer': player_data.get(underperformer_id, {}).get('name', 'Unknown') if underperformer_id else 'Unknown',
            'Underperformer Points': min_points,
            'Formation': formation,
            'Defensive Points': defensive_points,
            'Attacking Points': attacking_points,
            'Chip Used': chip_used,
            'Performance vs Avg': gw_performance_vs_avg,
            'autosub_details': autosub_details,
            'autosub_points': autosub_points
        })

        return team_gameweek_data_list
    except Exception as e:
        raise DataProcessingError(
            f"Error processing detailed gameweek data for team",
            context="get_detailed_gw_data"
        ) from e

def get_differential_king(league_data: Dict[str, Any], gameweek: int, player_data: Dict[int, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    try:
        player_ownership: Dict[int, List[str]] = {} 
        for manager_data in league_data['standings']['results']:
            manager_name = manager_data['entry_name']
            gw_picks = manager_data['gameweek_data'].get(str(gameweek), {}).get('picks', [])
            for pick in gw_picks:
                player_id = pick['element']
                if player_id not in player_ownership:
                    player_ownership[player_id] = []
                player_ownership[player_id].append(manager_name)

        differential_players: List[Dict[str, Any]] = []
        for player_id, owners in player_ownership.items():
            if len(owners) == 1: 
                player_name = player_data.get(player_id, {}).get('name', 'Unknown Player')
                player_points_val = player_data.get(player_id, {}).get('points', 0)
                differential_players.append({
                    'player_id': player_id,
                    'player_name': player_name,
                    'points': player_points_val,
                    'owner': owners[0] 
                })

        if differential_players:
            differential_king = max(differential_players, key=lambda x: x['points'])
            return differential_king
        else:
            return None 
    except Exception as e:
        raise DataProcessingError(
            f"Error finding differential king for gameweek {gameweek}",
            context="get_differential_king"
        ) from e

def process_gameweek_for_league(league_data: Dict[str, Any], player_data: Dict[int, Dict[str, Any]], gameweek: int, all_time_stats_manager: Any) -> None:
    try:
        for entry in league_data['standings']['results']:
            team_name = entry['entry_name']
            team_gameweek_data_list = get_detailed_gw_data(league_data, entry, player_data, gameweek)
            
            # Skip if no data for this gameweek
            if not team_gameweek_data_list:
                continue
                
            team_gameweek_data = team_gameweek_data_list[0]
            
            try:
                autosub_details = team_gameweek_data.get('autosub_details', [])
                for autosub in autosub_details:
                    player_name = autosub.get('player_in_name', 'Unknown')
                    points = autosub.get('points_gained', 0)
                    all_time_stats_manager.update_best_autosub_cameo(team_name, gameweek, player_name, points)
            except Exception as e:
                print(f"Warning: Error processing autosub data for team {team_name}: {str(e)}")
            
            try:
                differential_king = get_differential_king(league_data, gameweek, player_data)
                all_time_stats_manager.process_differential_king(differential_king)
            except Exception as e:
                print(f"Warning: Error processing differential king for team {team_name}: {str(e)}")

            try:
                all_time_stats_manager.update_all_stats_for_manager(
                    team_gameweek_data,
                    team_name,
                    gameweek
                )
            except Exception as e:
                print(f"Warning: Error updating stats for team {team_name}: {str(e)}")
    except Exception as e:
        raise DataProcessingError(
            f"Error processing gameweek {gameweek} for league",
            context="process_gameweek_for_league"
        ) from e
