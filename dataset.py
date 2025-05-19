#higher score = higher category = more depressed
import math
import random
import os
import pandas as pd
import numpy as np
import torch

random.seed(1)

def get_age(x):
    return 2025 - x

def encode_bool(x):
    if x:
        return 1
    else:
        return 0

def extract_participant_id(x):
    return x.split("_")[0]

def extract_response_id(x):
    return int(x.split("_")[1])

def largest_sublist(list_r):
    sublist = [list_r[0]]
    largest_sublist = []


    for i in range(1, len(list_r)):
        if list_r[i] - sublist[-1] == 1:
            sublist.append(list_r[i])

        else:
            sublist = [list_r[i]]

        if len(sublist) > len(largest_sublist):
            largest_sublist = sublist



    return largest_sublist

def filter_participants(df):

    d = {}
    for i in range(len(df["__index_level_0__"])):
        participant = df["__index_level_0__"].iloc[i].split("_")[0]

        if participant not in d:
            d[participant] = []

        response = df["__index_level_0__"].iloc[i].split("_")[1]
        d[participant].append(int(response))

    new_d = {}
    for participant in d:
        if len(d[participant]) >= 6:
            d[participant] = sorted(d[participant])

            sublist = largest_sublist(d[participant])

            if len(sublist) >= 6:

                new_d[participant] = sublist

    df["participant_id"] = df["__index_level_0__"].apply(extract_participant_id)
    df["response_id"] = df["__index_level_0__"].apply(extract_response_id)
    d_participant_to_rows = {}

    for participant in new_d:
        filtered_df = df[df['participant_id'] == participant]
        filtered_df_2 = []

        for i in range(len(filtered_df["response_id"])):
            response = filtered_df["response_id"].iloc[i]
            if response in new_d[participant]:
                filtered_df_2.append(filtered_df.iloc[i])

        filtered_df_2 = pd.DataFrame(filtered_df_2)
        filtered_df_2 = filtered_df_2.sort_values(by='response_id')

        d_participant_to_rows[participant] = filtered_df_2

    return d_participant_to_rows



def preprocess(df_primary):

    df_primary["age"] = df_primary['birthyear'].apply(get_age)
    df_primary.drop(["birthyear", "phq9_cat_end", "phq9_cat_start", "participant_id", "response_id"], axis=1, inplace=True)

    race_columns = ["race_white", "race_black", "race_hispanic", "race_asian", "race_other"]

    for col in race_columns:
        df_primary[col] = df_primary[col].apply(encode_bool)

    return df_primary


def test_train_val_split():
    #80 10 10 split
    participant_list = os.listdir("filtered_scaled")
    random.shuffle(participant_list)

    n = len(participant_list)



    train_set = participant_list[0: math.ceil(n*0.8)]
    test_set = participant_list[ math.ceil(n*0.8): math.ceil(n*0.9)]
    val_set = participant_list[math.ceil(n*0.9):]


    return train_set, test_set, val_set



def calc_mu_sigma(column):
    participant_list = os.listdir("filtered")
    vals = []
    for file in participant_list:
        df = pd.read_csv("filtered/" + file)

        vals += df[column].dropna().tolist()


    vals = np.array(vals)
    return np.mean(vals), np.std(vals)

def scale(file, file_loc):


    df_main = pd.read_csv(file_loc)
    df_scales = pd.read_csv("col_mean_sd.csv")


    for i in range(len(df_scales["Mean"])):
        mean = df_scales["Mean"].iloc[i]
        sd = df_scales["SD"].iloc[i]
        col = df_scales["Column"].iloc[i]

        def z_score(x):
            return (x - mean)/sd

        df_main[col]  = df_main[col].apply(z_score)

    df_main.to_csv("filtered_scaled/" + file, index=False)

if __name__ == "__main__":
    files = os.listdir("filtered")
    for file in files:
        scale(file=file, file_loc="filtered/0.csv")
        print(file)

    '''
    df = pd.DataFrame()

    cols = pd.read_csv("filtered/0.csv").columns.tolist()

    cols.remove("__index_level_0__")
    means = []
    sds = []

    for col in cols:
        mean, sd = calc_mu_sigma(col)
        means.append(mean)
        sds.append(sd)
        print(col, mean, sd)

    df["Column"] = cols
    df["Mean"] = means
    df["SD"] = sds

    df.to_csv("col_mean_sd.csv", index=False)
    
    '''