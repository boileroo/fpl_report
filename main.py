from functions.data_operations import fetch_and_save_raw_data, load_data_and_create_mappings, get_formatted_league_name
from functions.report_generation import generate_analysis_report, save_report_to_file

def main():
    gameweek = input("Please enter the current gameweek: ")
    league_id = input("Please enter the league id: ")
    
    mini_league_file, player_data_file = fetch_and_save_raw_data(gameweek, league_id)

    mini_league_data, player_id_to_name, player_id_to_points, player_id_to_position = load_data_and_create_mappings(mini_league_file, player_data_file)
    league_name = get_formatted_league_name(mini_league_data)
    
    output_content = generate_analysis_report(gameweek, mini_league_data, player_id_to_name, player_id_to_points, player_id_to_position)
    save_report_to_file(output_content, gameweek, league_name)

if __name__ == "__main__":
    main()