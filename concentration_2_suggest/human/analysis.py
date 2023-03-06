import pandas as pd
from path import Path

import csv
import os
import time
import json
import datetime
import math


ids = []
mod = []
turns = []
time_play = []
avg_time_until_match = []
number_of_rc_suggestions = []
number_of_card_suggestion = []
total_number_of_suggestions = []
number_of_suggestion_for_first_card = []
number_of_suggestions_followed = []
number_of_card_suggestion_not_followed = []
number_of_row_column_suggestion_not_followed = []
number_of_suggestions_for_first_card_not_followed = []
suggestion_first_card_with_match_in_next_turn = []
wrong_suggestions = []  # not all wrong suggestions, just those the user should have noticed 
                        #i.e the robot suggest a wrong card and user click another card and found a pair or the user click the card suggested and doesn't match


def get_turn_number(df):
    """
    get number of turns necessary to end a game for each user
    """
    
    tmp = df.loc[df['game_ended'] == True]
    elem = tmp['turn_number'].iloc[0]    
    print("turns:", elem)      
    turns.append(elem)


def get_time(df):
    tmp = df.loc[df['match'] == True]
    tmp = tmp['time_until_match'].tolist()
    print("time list:", tmp)
    mysum = datetime.timedelta()
    for i in tmp:
        (m, s) = i.split(':')
        d = datetime.timedelta(minutes=int(m), seconds=int(s))
        mysum += d
    time_play.append(str(mysum))
    print("time play:", str(mysum))
    
    avg = (str(datetime.timedelta(seconds=math.trunc(sum(map(lambda f: int(f[0])*60 + int(f[1]), map(lambda f: f.split(':'), tmp)))/len(tmp)))))
    avg_time_until_match.append(avg)
    print("avg time until match:", avg)


def calculate_suggestions(df):
    tmp = df.loc[df['suggestion_type'] != 'none']
    tmp = tmp['suggestion_type'].tolist()
    total_number_of_suggestions.append(len(tmp))
    print("number of suggestions:", len(tmp))

    tmp = df.loc[df['suggestion_type'] == 'card']
    tmp = tmp['suggestion_type'].tolist()
    number_of_card_suggestion.append(len(tmp))
    print("number of card suggestions:", len(tmp))

    tmp = df.loc[(df['suggestion_type'] == 'row') | (df['suggestion_type'] == 'column')]
    tmp = tmp['suggestion_type'].tolist()
    number_of_rc_suggestions.append(len(tmp))
    print("number of row/column suggestions:", len(tmp))

    tmp = df.loc[(df['turn_number'] % 2 != 0) & (df['suggestion_type'] != 'none')]
    tmp = tmp['suggestion_type'].tolist()
    number_of_suggestion_for_first_card.append(len(tmp))
    print("number of suggestions for first card:", len(tmp))

    tmp = df.loc[(df['suggestion_type'] == 'card') & (df['turn_number'] % 2 == 0) & \
         (((df['position_clicked'] == df['position_suggested']) & (df['match'] == False)) | ((df['position_clicked'] != df['position_suggested']) & (df['match'] == True)))]
    wrong_suggestions.append(len(tmp))
    print("number of wrong suggestions that the user should have noticed:", len(tmp))


def followed_suggestions(df):
    suggestions_followed = 0

    tmp = df.loc[(df['suggestion_type'] == 'card') & (df['position_clicked'] == df['position_suggested'])]
    suggestions_followed = len(tmp)

    tmp = df.loc[(df['suggestion_type'] == 'row') & (df['position_clicked'].str[1] == df['position_suggested'])]
    suggestions_followed += len(tmp)

    tmp = df.loc[(df['suggestion_type'] == 'column') & (df['position_clicked'].str[4] == df['position_suggested'])]
    suggestions_followed += len(tmp)

    print("suggestion followed:", suggestions_followed)
    number_of_suggestions_followed.append(suggestions_followed)

    # check if has followed the suggestion for first card and then if a pair has been found
    tmp = df.loc[(df['suggestion_type'] == 'card') & (df['position_clicked'] == df['position_suggested']) & (df['turn_number'] % 2 != 0) & (df['match'].shift(-1) == True)]
    print("suggestion for the first card followed that led to a match:", len(tmp))
    suggestion_first_card_with_match_in_next_turn.append(len(tmp))
    

def suggestions_not_followed(df):
    tmp = df.loc[(df['suggestion_type'] == 'card') & (df['position_clicked'] != df['position_suggested'])]
    number_of_card_suggestion_not_followed.append(len(tmp))
    print("card not followed", len(tmp))

    row_col_not_followed = 0
    tmp = df.loc[(df['suggestion_type'] == 'row') & (df['position_clicked'].str[1] != df['position_suggested'])]
    row_col_not_followed += len(tmp)
    tmp = df.loc[(df['suggestion_type'] == 'column') & (df['position_clicked'].str[4] != df['position_suggested'])]
    row_col_not_followed += len(tmp)
    print("row/col not followed", row_col_not_followed)
    number_of_row_column_suggestion_not_followed.append(row_col_not_followed)

    tmp = df.loc[(df['suggestion_type'] == 'card') & (df['position_clicked'] != df['position_suggested']) & (df['turn_number'] % 2 != 0)]
    number_of_suggestions_for_first_card_not_followed.append(len(tmp))
    print("first card not followed", len(tmp))

    time.sleep(1)


# get all csv 
path ="plot\\"
df_append = pd.DataFrame()
for root, dirs, files in sorted(os.walk(path)):
    for file in files:
        if(file.endswith(".csv")):
            print(os.path.join(root,file))
            # one data frame for file
            df = pd.read_csv(os.path.join(root,file), sep=';')
            print(df)

            # get id and mod
            ids.append(df['id_player'].iloc[0])
            mod.append(df['robot_type'].iloc[0])

            # get turn number
            get_turn_number(df)

            # get time
            get_time(df)

            # get number of suggestion
            calculate_suggestions(df)

            # check if user followed the suggestion
            followed_suggestions(df)

            # get all suggestions that user has not followed
            suggestions_not_followed(df)

            
print("\n\nid:", ids)
print("\nrobot_type:", mod)
print("\nturns:", turns)
print("\ntime:", time_play)
print("\navg_time_until_match", avg_time_until_match)
print("\ncard_suggestion", number_of_card_suggestion)
print("\nrow_column_suggestion", number_of_rc_suggestions)
print("\nn_suggestion:", total_number_of_suggestions)
print("\nsuggestion for the first_card", number_of_suggestion_for_first_card)
print("\nnumber of suggestion followed:", number_of_suggestions_followed)
print("\ncard not followed", number_of_card_suggestion_not_followed)
print("\nrow_col not followed", number_of_row_column_suggestion_not_followed)
print("\nfirst card not followed", number_of_suggestions_for_first_card_not_followed)
print("\nsuggestion_first_card_with_match_in_next_turn", suggestion_first_card_with_match_in_next_turn)
print("\nwrong suggestion that user should have noticed:", wrong_suggestions)

csv_struct = {
    "id": [],
    "robot_type": [],
    "turns": [],
    "time to finish": [],
    "average time to find a pair": [],
    "number of suggestions": [],
    "number of card suggestions": [],
    "number of row/col suggestions": [],
    "number of suggestions for first card": [],
    "number of suggestions followed": [],
    "number of card suggestions not followed": [],
    "number of row/col suggestions not followed": [],
    "number of suggestions for first card not followed": [],
    "suggestions for the first card that let to a match": [],
    "wrong suggestions": []
}

csv_struct['id'] = ids
csv_struct['robot_type'] = mod
csv_struct['turns'] = turns
csv_struct['time to finish'] = time_play
csv_struct['average time to find a pair'] = avg_time_until_match
csv_struct['number of suggestions'] = total_number_of_suggestions
csv_struct['number of card suggestions'] = number_of_card_suggestion
csv_struct['number of row/col suggestions'] = number_of_rc_suggestions
csv_struct['number of suggestions for first card'] = number_of_suggestion_for_first_card
csv_struct['number of suggestions followed'] = number_of_suggestions_followed
csv_struct['number of card suggestions not followed'] = number_of_card_suggestion_not_followed
csv_struct['number of row/col suggestions not followed'] = number_of_row_column_suggestion_not_followed
csv_struct['number of suggestions for first card not followed'] = number_of_suggestions_for_first_card_not_followed
csv_struct['suggestions for the first card that let to a match'] = suggestion_first_card_with_match_in_next_turn
csv_struct['wrong suggestions'] = wrong_suggestions

print("************* STRUCT ************")
print(json.dumps(csv_struct, default=str, indent=3))

file_path = Path("../human/plot/results.csv")
keys = csv_struct.keys()

with open(file_path, "a+", newline='') as outfile:
    writer = csv.writer(outfile, delimiter = ";")
    writer.writerow(keys)
    writer.writerows(list(zip(*[csv_struct[key] for key in keys])))
