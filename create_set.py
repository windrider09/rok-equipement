#!/usr/bin/env python3

import json
import pandas as pd
from itertools import product
import argparse

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

def flatten_dict_columns(df):
    """
    Recursively flatten columns containing dictionaries into multiple columns with numerical values.

    Args:
        df (pd.DataFrame): Input DataFrame with columns containing dictionaries.

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
    for column in df.columns:
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

def cal_stat(df):
    stats = [{}] * len(df)
    for index, row in df.iterrows():
        for slot in df.columns:
            stats[index] = add_dicts(stats[index], json.load(open(f'./rawData/{slot}.json','r'))[row[slot]]['stats'])
    df['stats'] = stats
    return df


def main(output_file=None):
    slots = ['weapon', 'helmet', 'chest', 'glove', 'leg', 'boot']
    json_files = [f'./rawData/{slot}.json' for slot in slots]
    combinations = get_combinations(json_files)

    if combinations:
        df = pd.DataFrame(combinations, columns = slots )
        df = cal_stat(df)
        df = flatten_dict_columns(df)
        print(f'{len(df)} sets created')
        # Sort by a specific column
        df.sort_values(by=['archer health', 'archer defense', 'archer attack'], ascending=False, inplace=True, ignore_index=True)
        print('Best archer set (prioritize health, defense, then finally attack):')
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
