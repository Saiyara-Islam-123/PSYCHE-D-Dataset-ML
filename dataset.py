#higher score = higher category = more depressed
import pandas as pd

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


if __name__ == "__main__":

    df = pd.read_csv("data.csv")

    d = (filter_participants(df))

    for participant in d:
        response_df = d[participant]
        response_df = preprocess(response_df)
        response_df.to_csv("filtered/" + participant+".csv", index=False)