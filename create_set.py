#!/usr/bin/env python3

import json
import pandas as pd
from itertools import product
import argparse
from collections import Counter



slots_global = ['weapon', 'helmet', 'chest', 'glove', 'leg', 'boot']
material_cost_multiplier = {'Normal': 1, 'Advanced': 4, 'Elite': 16, 'Epic': 64, 'Legendary': 256}
# slots_global = ['weapon_base', 'helmet_base', 'chest_base', 'glove_base', 'leg_base', 'boot_base']

def load_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON in file '{file_path}': {e}")
        return []

def add_dicts(dict1, dict2):
    result = {}
    # Iterate through keys in dict1
    for key in dict1:
        if key in dict2:
            if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                # If both values are dictionaries, recursively call add_dicts
                result[key] = add_dicts(dict1[key], dict2[key])
            else:
                # If both values are not dictionaries, add them
                result[key] = dict1[key] + dict2[key]
        else:
            # If the key is only in dict1, copy its value
            result[key] = dict1[key]
    
    # Iterate through keys in dict2 to check for keys not in dict1
    for key in dict2:
        if key not in dict1:
            # If the key is only in dict2, copy its value
            result[key] = dict2[key]
    
    return result

def add_dicts(dict1, dict2):
    # Check if dict1 is empty
    if not bool(dict1):
        return dict2
    
    # Check if dict2 is empty
    if not bool(dict2):
        return dict1

    result = {}
    
    # Iterate through keys in dict1
    for key in dict1:
        if key in dict2:
            if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                # If both values are dictionaries, recursively call add_dicts
                result[key] = add_dicts(dict1[key], dict2[key])
            else:
                # If both values are not dictionaries, add them
                result[key] = dict1[key] + dict2[key]
        else:
            # If the key is only in dict1, copy its value
            result[key] = dict1[key]
    
    # Iterate through keys in dict2 to check for keys not in dict1
    for key in dict2:
        if key not in dict1:
            # If the key is only in dict2, copy its value
            result[key] = dict2[key]
    
    return result

def flatten_dict_column(df, column_name=None):
    """
    Recursively flatten a column containing dictionaries into multiple columns with numerical values.

    Args:
        df (pd.DataFrame): Input DataFrame.
        column_name (str, optional): The name of the column containing dictionaries to be flattened.
            If None, all columns with dictionaries will be flattened.

    Returns:
        pd.DataFrame: New DataFrame with flattened columns.
    """
    def flatten_dict(d, prefix=''):
        flattened = {}
        for key, value in d.items():
            if isinstance(value, dict):
                flattened.update(flatten_dict(value, prefix + key + ' '))
            else:
                flattened[prefix + key] = value
        return flattened

    new_df = df.copy()

    if column_name is None:
        # Flatten all columns with dictionaries
        columns_to_flatten = [col for col in df.columns if df[col].apply(lambda x: isinstance(x, dict)).all()]
    else:
        columns_to_flatten = [column_name]

    for column in columns_to_flatten:
        if df[column].apply(lambda x: isinstance(x, dict)).all():
            # Convert the column to JSON strings for easy parsing
            new_df[column] = df[column].apply(json.dumps)

            # Parse JSON strings into dictionaries
            new_df[column] = new_df[column].apply(json.loads)

            # Flatten dictionaries recursively
            flattened_dicts = new_df[column].apply(flatten_dict)

            # Create new DataFrame with flattened columns
            flattened_df = pd.DataFrame(flattened_dicts.tolist())

            # Concatenate the flattened DataFrame with the original DataFrame
            new_df = pd.concat([new_df, flattened_df], axis=1)

            # Drop the original column with dictionaries
            new_df.drop(column, axis=1, inplace=True)

    return new_df

def get_combinations(json_files):
    # Load JSON data from each file and store them in a list
    json_data_list = [load_json_file(file_path) for file_path in json_files]

    # Use itertools.product to generate combinations
    combinations = list(product(*json_data_list))

    return combinations

def get_cost(df):
    cost = [{}] * len(df)
    for index, row in df.iterrows():
        for slot in df.columns:
            if slot in slots_global:
                equipment_piece_cost = json.load(open(f'./rawData/{slot}.json','r'))[row[slot]]['cost']
                equipment_tier = json.load(open(f'./rawData/{slot}.json','r'))[row[slot]]['tier']
                cost[index] = add_dicts(cost[index], equipment_piece_cost)
                cost[index]['material'] = material_cost_multiplier[equipment_tier] * (
                        cost[index]['leather']+
                        cost[index]['ebony']+
                        cost[index]['iron']+
                        cost[index]['bone'])
                del cost[index]['leather']
                del cost[index]['iron']
                del cost[index]['ebony']
                del cost[index]['bone']

    df['cost'] = cost 
    return df

def get_stat(df):
    stats = [{}] * len(df)
    for index, row in df.iterrows():
        for slot in df.columns:
            if slot in slots_global:
                equipment_piece_stat = json.load(open(f'./rawData/{slot}.json','r'))[row[slot]]['stats']
                stats[index] = add_dicts(stats[index], equipment_piece_stat)
    df['stats'] = stats
    return df

def get_set(df):
    # Define a function to extract the set name from a JSON file
    def get_set_name(row, slot):
        return json.load(open(f'./rawData/{slot}.json','r'))[row[slot]]['set']
    
    # Function to count occurrences and create the dictionary
    def count_occurrences(lst):
        # Use Counter to count occurrences while omitting 'None'
        counts = Counter(item for item in lst if item is not None)
        return dict(counts)

    # Function to get set stats
    def get_set_stat(row):
        for set_name, set_count in row['sets'].items():
            set_stats = json.load(open('./rawData/set.json','r')).get(set_name,{}).get(str(set_count),{})
            if set_stats:
                row['stats'] = add_dicts(row['stats'], set_stats)
        return row

    # Apply the functions to each row and create new columns
    df['set_list'] = df.apply(lambda row: [get_set_name(row,slot) for slot in slots_global], axis = 1)
    df['sets'] = df['set_list'].apply(count_occurrences)
    df = df.apply(lambda row: get_set_stat(row), axis = 1)
    df = df.drop(['set_list'], axis=1)

    return df


def main(output_file=None):
    json_files = [f'./rawData/{slot}.json' for slot in slots_global]
    combinations = get_combinations(json_files)

    if combinations:
        df = pd.DataFrame(combinations, columns = slots_global )
        df = get_stat(df)
        df = get_set(df)
        df = get_cost(df)
        df = flatten_dict_column(df, 'cost')
        df = flatten_dict_column(df, 'stats')
        print(f'{len(df)} sets created')
        # Sort by a specific column
        df.sort_values(by=['archer health', 'archer defense', 'archer attack'], ascending=False, inplace=True, ignore_index=True)
        print('Best archer set (prioritize health, defense, then finally attack):')
        #print(df.head(1))
        print(df.iloc[0])

        # Save the DataFrame to a CSV file if an output file is provided
        if output_file:
            df.to_csv(output_file, index=False)
            print(f'DataFrame saved to {output_file}')

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate and analyze equipment sets.')
    parser.add_argument('--output', '-o', help='Output CSV file name (optional)')
    args = parser.parse_args()

    main(args.output)
