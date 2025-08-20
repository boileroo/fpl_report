def get_formatted_league_name(league_data):
    return league_data['league']['name'].replace(" ", "_").replace("/", "_").lower()
