# Names: Albert Carreno (acarreno@baseball-analytica.com) and Addison Kline (akline@baseball-analytica.com) 
# Date of creation: 2023-08-04
# File Description: This Python script was written by Addison Kline to scrape the relevant pickoff data from the given CSV files and create a new CSV file
# from that filtered data; the script for analyzing the data is separate.

import pandas as pd
import numpy as np
import os
import glob

# step 0: organize all CSVs into pandas dataframes
# I will concede that it's much easier to read multiple CSVs at a time in R than it is in Python
print("**Completing step 0...**")
path = os.getcwd() + "/smt_data_challenge_2023"
# get all csv files in the relevant directories
ball_pos_files = glob.glob(os.path.join(path + "/ball_pos", "*.csv")) 
game_events_files = glob.glob(os.path.join(path + "/game_events", "*.csv"))
game_info_files = glob.glob(os.path.join(path + "/game_info", "*.csv"))
# create and fill the four relevant dataframes
ball_pos = pd.DataFrame()
game_events = pd.DataFrame()
game_info = pd.DataFrame()
player_pos = pd.DataFrame()
for file in ball_pos_files:
    df = pd.read_csv(file)
    ball_pos = pd.concat([ball_pos, df], ignore_index=True)
for file in game_events_files:
    df = pd.read_csv(file)
    game_events = pd.concat([game_events, df], ignore_index=True)
for file in game_info_files:
    df = pd.read_csv(file)
    game_info = pd.concat([game_info, df], ignore_index=True)
# because of all of player_pos's subdirectories this has to be different
for root, dirs, files in os.walk(path + "/player_pos"):
    for file in files:
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(root, file))
            player_pos = pd.concat([player_pos, df], ignore_index=True)

# step 1: create game_play_id for each df
# basically, play ids are only unique for each game, so by making a new variable called game_play_id that concatenates game_str and play_id, we can make each play in the dataset completely unique
# e.g. if game_str = "1901_05_TeamLI_TeamA3" and play_id = 17, then game_play_id = "1901_05_TeamLI_TeamA3_17"
print("**Completing step 1...**")
ball_pos['game_play_id'] = ball_pos["game_str"].str.cat(ball_pos["play_id"].astype(str), sep = '_')
game_events['game_play_id'] = game_events["game_str"].str.cat(game_events["play_id"].astype(str), sep = '_')
game_info['game_play_id'] = game_info["game_str"].str.cat(game_info["play_per_game"].astype(str), sep = '_')
player_pos['game_play_id'] = player_pos["game_str"].str.cat(player_pos["play_id"].astype(str), sep = '_')

# step 2: compiling list of all valid pickoff plays
print("**Completing step 2...**")
# the list of all plays with event_code = 6 (pickoffs), yet to be filtered
pickoff_ids = pd.Series(game_events.loc[(game_events['event_code'] == 6) & (game_events['player_position'] == 1), 'game_play_id'].values)
# filter list of all pickoff plays to get just the valid ones for this analysis
pickoff_ids_corrected = []
for id in pickoff_ids.values:
    play = game_events.loc[game_events['game_play_id'] == id]
    if (play.shape[0] == 3): # check to see if pickoff has 3 rows in game_events
        if ( ((play.iloc[1]['player_position'] == 3 and play.iloc[1]['event_code'] == 2) and (play.iloc[2]['player_position'] == 0 and play.iloc[2]['event_code'] == 5))): # check to see if pickoff follows the "1 6, 3 2, 0 5" format (see paper for more details)
            if (game_info.loc[game_info['game_play_id'] == id].shape[0] > 0): # check to see if pickoff exists in game_info dataframe
                if (player_pos.loc[(player_pos['game_play_id'] == id) & (player_pos['player_position'] == 11)].shape[0] > 0): # check to see if first baseman info for pickoff exists in player_pos dataframe
                    # if all of the above conditions are met, add this pickoff to the filtered list of pickoffs
                    pickoff_ids_corrected.append(id)

pickoff_ids_corrected = pd.Series(pickoff_ids_corrected)

# steps 3-4: for each pickoff, determine whether or not it was successful and other info
print("**Completing steps 3 and 4...**")
# these are the variables that we'll be considering
pickoff_successful = np.zeros(pickoff_ids_corrected.size) # 1 if the runner is out, 0 otherwise
pickoff_time = np.zeros(pickoff_ids_corrected.size) # how many milliseconds elapsed in this pickoff
runner_distance = np.zeros(pickoff_ids_corrected.size) # how far the runner was from first base at their farthest
runner_max_x = np.zeros(pickoff_ids_corrected.size) # x coordinate of runner at their farthest from first base
runner_max_y = np.zeros(pickoff_ids_corrected.size) # y coordinate of runner at their farthest from first base
fielder_distance = np.zeros(pickoff_ids_corrected.size) # how far the first baseman was from first base at their farthest
fielder_max_x = np.zeros(pickoff_ids_corrected.size) # x coordinate of first baseman at their farthest from first base
fielder_max_y = np.zeros(pickoff_ids_corrected.size) # y coordinate of first baseman at their farthest from first base
for index, id in pickoff_ids_corrected.items():
    # step 3: for each pickoff, determine whether or not it was successful
    play = game_info.loc[game_info['game_play_id'] == id]
    play_index = game_info.loc[game_info['game_play_id'] == id].index[0]
    if (game_info.iloc[play_index + 1]['first_baserunner'] == 0):
        # if no runner is at first base in the play immediately following the pickoff, then the pickoff is deemed successful (given how the data is filtered, this is necessarily true)
        pickoff_successful[index] = 1
    # step 4: for each pickoff, determine the time it takes to complete the play
    play = player_pos[(player_pos['game_play_id'] == id) & (player_pos['player_position'] == 11)].reset_index()
    # pickoff time = play end timestamp - play start timestamp
    pickoff_time[index] = play.iloc[play.shape[0] - 1].get('timestamp') - play.iloc[0].get('timestamp')
    # step 4 part 2: now look at how far each runner was from the bag
    # the x,y coordinates of first base would be 90/sqrt(2), 90/sqrt(2) which is roughly 63.6396, 63.6396
    play['runner_distance'] = np.sqrt((play['field_x'] - 63.6396)**2 + (play['field_y'] - 63.6396)**2) # euclidean distance between runner and first base at each timestamp
    runner_distance[index] = play['runner_distance'].max() # find the runner's maximum distance from first base
    max_index = play['runner_distance'].idxmax()
    runner_max_x[index] = play.iloc[max_index].get('field_x') # runner x coord at max distance from first
    runner_max_y[index] = play.iloc[max_index].get('field_y') # runner y coord at max distance from first
    # step 4 part 3: now look at how far each first baseman was from the bag
    play = player_pos[(player_pos['game_play_id'] == id) & (player_pos['player_position'] == 3)].reset_index()
    play['fielder_distance'] = np.sqrt((play['field_x'] - 63.6396)**2 + (play['field_y'] - 63.6396)**2)
    fielder_distance[index] = play['fielder_distance'].max() # find the first baseman's maximum distance from first base
    max_index = play['fielder_distance'].idxmax()
    fielder_max_x[index] = play.iloc[max_index].get('field_x') # runner x coord at max distance from first
    fielder_max_y[index] = play.iloc[max_index].get('field_y') # runner y coord at max distance from first
 
pickoff_successful = pd.Series(pickoff_successful)
pickoff_time = pd.Series(pickoff_time)
runner_distance = pd.Series(runner_distance)
runner_max_x = pd.Series(runner_max_x)
runner_max_y = pd.Series(runner_max_y)
fielder_distance = pd.Series(fielder_distance)
fielder_max_x = pd.Series(fielder_max_x)
fielder_max_y = pd.Series(fielder_max_y)

print(fielder_distance)
print(fielder_max_x)
print(fielder_max_y)

# step 5: writing resulting data to a CSV file to be analyzed separately
print('**Completing step 5...**')
result = pd.DataFrame({
    "game_play_id": pickoff_ids_corrected,
    "pickoff_successful": pickoff_successful,
    "pickoff_time": pickoff_time,
    "runner_max_distance": runner_distance,
    "runner_max_x": runner_max_x,
    "runner_max_y": runner_max_y,
    "fielder_distance": fielder_distance,
    "fielder_max_x": fielder_max_x,
    "fielder_max_y": fielder_max_y
}).to_csv('pickoff_data.csv') # resulting data is written to a csv file in this folder called "pickoff_data.csv"

#print(ball_pos)
#print(game_events)
#print(game_info)
#print(player_pos)
