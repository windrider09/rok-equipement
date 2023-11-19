#!/usr/bin/env python3

import json

# Function to add "skill damage" and "counterattack damage" to an item
def add_new_stats(item, new_stat):
    item["stats"][new_stat] = 0  # You can set the desired value here

# Function to process a JSON file and update its contents
def process_json_file(file_path, new_stat):
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)

        # Loop through each item in the JSON data and add the fields
        for item_name, item_data in data.items():
            add_new_stats(item_data, new_stat)

        # Write the updated data back to the same file
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        print(f"Updated {file_path} successfully.")
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")

slots = ['weapon', 'helmet', 'chest', 'glove', 'leg', 'boot']
json_files = [f'./rawData/{slot}_base.json' for slot in slots]
 
# Loop through JSON files in the directory
for filename in json_files:
    process_json_file(filename, 'skill damage')
    process_json_file(filename, 'counterattack damage')
