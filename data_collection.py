import requests
import pandas as pd
import time
import json
import glob

# --- CONFIGURATION ---
API_KEY = "###################################" # replace with your API key
headers = {"X-Riot-Token": API_KEY}
ROUTING_REGION = "americas"
PLATFORM_REGION = "na1"

TIERS_TO_SCRAPE = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'EMERALD', 'DIAMOND']
DIVISIONS_TO_SCRAPE = ['I', 'II', 'III', 'IV']

PLAYERS_PER_RANK_PAGE = 50

MATCHES_PER_PLAYER = 15

print("--- Starting Data Collection Script ---")

# --- MAIN LOOP ---

try:
    # Iterate over each TIER
    for tier in TIERS_TO_SCRAPE:

        current_tier_data = []
        print(f"\n--- Processing Tier: {tier} ---")

        # Iterate over each DIVISION
        for division in DIVISIONS_TO_SCRAPE:

            current_rank = f"{tier} {division}"
            print(f"--- Processing Rank: {current_rank} ---")

            # Get Player List
            try:
                player_list_url = f"https://{PLATFORM_REGION}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{tier}/{division}"

                response_players = requests.get(player_list_url, headers=headers, params={'page': 1})
                response_players.raise_for_status() # Raise error if status is 4xx or 5xx

                player_list = response_players.json()
                player_list_sample = player_list[:PLAYERS_PER_RANK_PAGE]
                print(f"Successfully fetched {len(player_list_sample)} players for {current_rank}.")

            except requests.exceptions.RequestException as e:
                print(f"Error fetching player list for {current_rank}: {e}")
                time.sleep(10) # Wait 10s on an error and skip
                continue

            time.sleep(1.2) # API rate limit

            # Iterate over each PLAYER
            for player in player_list_sample:
                player_puuid = player['puuid']

                # Get Match List for Player
                try:
                    match_list_url = f"https://{ROUTING_REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{player_puuid}/ids"
                    response_matches = requests.get(match_list_url, headers=headers, params={'count': MATCHES_PER_PLAYER, 'queue': 420})
                    response_matches.raise_for_status()
                    match_ids = response_matches.json()

                except requests.exceptions.RequestException as e:
                    print(f"Error fetching match list for {player_puuid}: {e}")
                    time.sleep(1.2)
                    continue

                time.sleep(1.2) # API rate limit

                # Iterate over each MATCH ID
                for match_id in match_ids:

                    # Get Match Details
                    try:
                        print(f"Fetching details for match: {match_id} (Rank: {current_rank})")
                        match_details_url = f"https://{ROUTING_REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"

                        response_details = requests.get(match_details_url, headers=headers)
                        response_details.raise_for_status()
                        match_data = response_details.json()

                        # TRANSFORM DATA
                        for participant in match_data['info']['participants']:
                            player_data = {
                                'matchId': match_id,
                                'tier_scraped_from': tier,
                                'rank_scraped_from': current_rank,
                                'championName': participant['championName'],
                                'teamId': participant['teamId'],
                                'win': participant['win']
                            }
                            # Add to the CURRENT TIER'S list
                            current_tier_data.append(player_data)

                    except requests.exceptions.RequestException as e:
                        print(f"Error fetching match details for {match_id}: {e}")

                    time.sleep(1.2) # API rate limit

        # SAVE DATA FOR THE TIER
        print(f"\n--- Finished collecting data for {tier} ---")
        if not current_tier_data:
            print(f"No data was collected for {tier}. Skipping save.")
            continue

        print(f"Collected {len(current_tier_data) // 10} matches for {tier}.")

        # Convert this tier's data to a DataFrame
        df_tier = pd.DataFrame(current_tier_data)

        # Save it to its own CSV file
        output_filename = f"lol_match_data_{tier}.csv"
        df_tier.to_csv(output_filename, index=False)

        print(f"--- SUCCESS! ---")
        print(f"Data for {tier} saved to {output_filename}")


except KeyboardInterrupt:
    print("\nScript interrupted by user. Exiting...")

print("\n--- SCRIPT FINISHED ---")


print("--- Starting Final Prep Script ---")

# --- FIND AND COMBINE ALL CSVs ---
# Find all files that match the pattern
all_csv_files = glob.glob('lol_match_data_*.csv')
print(f"Found files: {all_csv_files}")

# Read each CSV and store it in a list of DataFrames
df_list = []
for file in all_csv_files:
    df_list.append(pd.read_csv(file))

# Combine them into one giant DataFrame
df = pd.concat(df_list, ignore_index=True)

print(f"\n--- Combined All Data ---")
print(f"Total rows in master dataset: {len(df)}")


# --- RUN ANALYSIS ---
# Calculate 'meta_score' for each champion
print("Calculating champion win rates...")
meta_score_map = df.groupby('championName')['win'].mean().to_dict()
df['meta_score'] = df['championName'].map(meta_score_map)

# Calculate team meta scores
print("Calculating team meta scores...")
team_scores = df.groupby(['matchId', 'tier_scraped_from', 'rank_scraped_from', 'teamId'])['meta_score'].sum().reset_index()

# Pivot the data
print("Pivoting data...")
team_scores_pivot = team_scores.pivot(
    index=['matchId', 'tier_scraped_from', 'rank_scraped_from'],
    columns='teamId',
    values='meta_score'
).reset_index()
team_scores_pivot.columns.names = [None]
team_scores_pivot = team_scores_pivot.rename(
    columns={100: 'blue_meta_score', 200: 'red_meta_score'}
)

# Get match winners
print("Merging winner data...")
match_winners = df[df['teamId'] == 100].groupby('matchId')['win'].first()
analysis_df = team_scores_pivot.merge(match_winners, on='matchId')
analysis_df = analysis_df.rename(columns={'win': 'did_blue_team_win'})

# Define core logic function
def get_meta_winner(row):
    if row['blue_meta_score'] > row['red_meta_score']:
        return row['did_blue_team_win']
    elif row['red_meta_score'] > row['blue_meta_score']:
        return not row['did_blue_team_win']
    else:
        return None

print("Calculating final 'did_meta_team_win' column...")
analysis_df['did_meta_team_win'] = analysis_df.apply(get_meta_winner, axis=1)

# Drop rows where scores were tied
analysis_df = analysis_df.dropna(subset=['did_meta_team_win'])

# --- SAVE THE FINAL FILE FOR TABLEAU ---
output_filename = 'final_analysis_for_tableau.csv'
columns_to_save = [
    'matchId',
    'tier_scraped_from',
    'rank_scraped_from',
    'did_meta_team_win'
]
analysis_df[columns_to_save].to_csv(output_filename, index=False)

print(f"\n--- SUCCESS! ---")
print(f"Final analysis-ready file saved as: {output_filename}")
print("Download this one file and open it in Tableau.")
