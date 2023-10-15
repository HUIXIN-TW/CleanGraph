import os
import sys
import json
from . import gpt_model
from . import web_crawler


# Entire /src/ Folder put int /llm/ folder here (TBC)
# import Crawler
# import GPTmodel

# Step 0: Get the input from the user
# Step 1: Run the crawler, then generate a .txt file under tmp
# Step 2: Run GPT model, then generate a userdata.js file under client/src/shared/userdata.js
# Step 3: Clear the tmp folder


def read_user_input():
    # Check if an argument was provided
    if len(sys.argv) > 1:
        input_value = sys.argv[1]
    else:
        input_value = "No input value provided."
    print(f"Input value: {input_value}")
    return input_value


def call_llm(file_path):
    print("Running GPT Model...")
    model_name = "ft:gpt-3.5-turbo-0613:uwa-csse:uwa-dataset:84kffWR6"
    initial_prompt_chunk_path = "initial_prompts.txt"
    gpt = gpt_model.GPTModel(model_name, file_path, initial_prompt_chunk_path)
    gpt.main()


# Define your function call_llm
def call_llm_folder(folder_path):
    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Check if the item is a file (not a directory)
        if os.path.isfile(file_path):
            # Call your function with the file path
            print(f"Processing file: {file_path}")
            call_llm(file_path)


def combine_triple_results(folder_path, combined_file_path):
    # Initialize an empty list to store combined data
    combined_data = []

    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            
            # Read the content of the JSON file
            with open(file_path, 'r') as file:
                data = json.load(file)
            
            # Append the data to the combined_data list
            combined_data.extend(data)

            # Delete the file
            os.remove(file_path)

    # Serialize the combined data to JavaScript format
    js_data = json.dumps(combined_data, indent=2, separators=(',', ': '))

    # Write the combined data to a JavaScript file
    with open(combined_file_path, 'w') as combined_file:
        combined_file.write(f'const UserData = {js_data};')

    print(f"Combined JSON files saved as '{combined_file_path}'")


def execute(input_value):
    print("Running script...")
    txt_folder_path = "txt_results"
    triple_folder_path = "triple_results"
    combined_file_path = "../client/src/shared/userdata.js"
    urls = input_value.split()

    for url in urls:
        print(url)
        web_crawler.generateTxt(url)

    call_llm_folder(txt_folder_path)

    combine_triple_results(triple_folder_path, combined_file_path)
    print("Done!")

if __name__ == "__main__":
    input_value = read_user_input()
    execute(input_value)


