#!/usr/bin/env python3

import json
from math import ceil

def special_talent_stats(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "stats" and isinstance(value, dict):
                # Recursively update values under the "stats" key
                data[key] = special_talent_stats(value)
            elif isinstance(value, (int, float)):
                # special talent stats
                data[key] = value + ceil(ceil(value/0.5)*0.3)*0.5
            elif isinstance(value, dict) or isinstance(value, list):
                # Recursively process nested dictionaries or lists
                data[key] = special_talent_stats(value)
    elif isinstance(data, list):
        # Recursively process list elements
        data = [special_talent_stats(item) for item in data]
    return data


def add_suffix(input_dict, suffix):
    # Create an empty result dictionary
    renamed_dict= {}
    
    # Iterate through the items in the input dictionary
    for key, value in input_dict.items():
        renamed_key = key+suffix
        renamed_dict[renamed_key] = value

    return renamed_dict



def process_and_save_json(input_file, output_file):
    try:
        # Open the input JSON file for reading
        with open(input_file, 'r') as file:
            original_data = json.load(file)

        # Create a deep copy of the original data to avoid modifying it
        special_data = json.loads(json.dumps(original_data))
        special_data = add_suffix(special_data, ' - special talent')

        # Multiply numerical values under "stats" dictionaries
        special_talent_stats(special_data)
        
        original_data.update(special_data)
        
        # Open the output JSON file for writing
        with open(output_file, 'w') as file:
            # Save both the original and modified data
            json.dump(original_data, file, indent=4)

        print(f"Successfully processed and saved to {output_file}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


# ceil(ceil(stat_value/0.5)*0.3)*0.5
if __name__ == "__main__":
    slots = ['weapon', 'helmet', 'chest', 'glove', 'leg', 'boot']
    for slot in slots:
        process_and_save_json(f'./rawData/{slot}_base.json', f'./rawData/{slot}.json')
