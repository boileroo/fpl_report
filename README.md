# FPL Analysis Script

This Python script (`main.py`) provides detailed analysis for Fantasy Premier League (FPL) mini-leagues. It fetches data from the official FPL API, processes it, and generates a comprehensive report for each manager in your mini-league.

## Features

- Fetches up-to-date data for a specific gameweek and mini-league
- Provides detailed statistics for each manager, including:
  - Points and rank
  - Captain and vice-captain performance
  - Transfers and costs
  - Team value and bank
  - Top scorer and underperformer
  - Formation and point distribution (defensive vs. attacking)
  - Chip usage
  - Performance vs. league average
  - Rank movement
- Generates a league standings table
- Saves all analysis to a text file for easy sharing and reference
- Allows multiple runs during a gameweek, always providing the most current data

## Requirements

- Python 3.6+
- `requests` library

## Installation

1. Clone this repository or download the script (`main.py`).
2. Install the required library:

   ```
   pip install requests
   ```

## Usage

1. Run the script:

   ```
   python main.py
   ```

2. When prompted, enter:
   - The current gameweek number
   - Your mini-league ID (you can find this in the URL when viewing your mini-league on the FPL website)

3. The script will fetch the latest data and perform the analysis.

4. Results will be displayed in the console and saved to a file named `league_analysis_gw{X}.txt`, where `{X}` is the gameweek number.

## Data Storage and Updates

The script creates two directories to store data:

- `player_data/`: Contains general player information for each gameweek
- `league_data/`: Contains mini-league specific data for each gameweek

Each time you run the script:
- It fetches new data, overwriting any existing files for the current gameweek.
- It generates a new analysis based on the most recent data.
- It overwrites the previous analysis file for that gameweek.

This allows you to run the script multiple times throughout a gameweek to get the most up-to-date analysis as matches are played and scores are updated.

## Note

This script uses the official FPL API, which has rate limits. Please use responsibly and avoid making excessive requests in a short period.

## Customization

You can modify the `get_detailed_gw_data` function in `main.py` to add or remove statistics based on your preferences. The main output formatting is done in the `main` function, which you can also customize to change the output style.

## Contributing

Feel free to fork this repository and submit pull requests with any enhancements. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is open source and available under the [MIT License](https://opensource.org/licenses/MIT).
