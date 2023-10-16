import os
import sys
import json
import shutil
from pathlib import Path
# from . import gpt_model
# from . import crawler_degree
# from . import crawler_unit
import gpt_model
import crawler_degree
import crawler_unit


def read_user_input():
    # Check if an argument was provided
    if len(sys.argv) > 1:
        input_value = sys.argv[1]
    else:
        input_value = "No input value provided."
    print(f"Input value: {input_value}")
    return input_value


def process_file_gpt(file_path: str, triple_folder_path: str) -> None:
    """
    Calls the GPT model on the specified file.

    Args:
        file_path (str): Path to the file to be processed.
    """
    print(f"Running GPT Model on file: {file_path}...")

    model_name = "ft:gpt-3.5-turbo-0613:uwa-csse:uwa-dataset:84kffWR6"
    initial_prompt_chunk_path = (
        Path("initial_prompts.txt").read_text().strip()
    )

    gpt = gpt_model.GPTModel(
        model_name, file_path, initial_prompt_chunk_path, triple_folder_path
    )
    gpt.main()


def process_folder(folder_path: str, triple_folder_path: str) -> None:
    """
    Processes all files in the specified folder with the GPT model.

    Args:
        folder_path (str): Path to the directory containing files to be processed.
        triple_folder_path (str): Path to the directory to save the triple results.
    """
    print(f"Processing files in folder: {folder_path}...")

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if os.path.isfile(file_path):
            try:
                process_file_gpt(file_path, triple_folder_path)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")


def combine_triple_results(folder_path: str, combined_file_path: str) -> None:
    """
    Combine the contents of all JSON files in a specified folder and save
    the combined data to a specified output file.

    Args:
        folder_path (str): Path to the directory containing JSON files.
        combined_file_path (str): Path to save the combined JSON data.
    """
    combined_data = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            print(f"Processing file: {file_path}")

            data = read_json_file(file_path)
            if data:
                combined_data.extend(data)

    write_to_json(combined_data, combined_file_path)
    print(f"Combined JSON files saved as '{combined_file_path}'")


def read_json_file(file_path: str) -> list:
    """Reads a JSON file and returns its content as a list."""
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []


def write_to_json(data: list, output_path: str) -> None:
    """Writes a list to a JSON file."""
    try:
        with open(output_path, "w") as outfile:
            json.dump(data, outfile, indent=2)
    except Exception as e:
        print(f"Error writing to {output_path}: {e}")


# https://handbooks.uwa.edu.au/coursedetails?code=62510 https://handbooks.uwa.edu.au/unitdetails?code=CITS1003
def execute(input_value, txt_folder_path, triple_folder_path, combined_file_path):
    """
    Process and visualize URLs based on their segments.

    Args:
        input_value (str): String containing space-separated URLs.
        txt_folder_path (str): Path to the text files folder.
        triple_folder_path (str): Path to the triple files folder.
        combined_file_path (str): Path to save the combined JSON data.

    Returns:
        str: Path to the knowledge graph visualization.
    """
    urls = input_value.split()

    for url in urls:
        segment = url.split("/")[-1].split("?")[0]
        print(f"web crawler: {url}")

        try:
            if segment == "unitdetails":
                crawler_unit.generateTxt(url)
            elif segment == "coursedetails":
                crawler_degree.generateTxt(url)
            else:
                print("Invalid URL")
        except Exception as e:
            print(f"Error processing {url}: {e}")

    try:
        process_folder(txt_folder_path, triple_folder_path)
        combine_triple_results(triple_folder_path, combined_file_path)
    except Exception as e:
        print(f"Error during processing: {e}")


def delete_folder(path: str) -> None:
    """
    Delete a folder and all its contents.

    Args:
        path (str): Path to the folder to be deleted.
    """
    try:
        shutil.rmtree(path)
        print(f"Deleted folder: {path}")
    except Exception as e:
        print(f"Error deleting folder {path}: {e}")


if __name__ == "__main__":
    txt_folder_path = "crawler_results"
    triple_folder_path = "triple_results"
    combined_file_path = "combined_triple_results.json"

    try:
        # input_value = input("Enter one or more space-separated URLs to process:\n")
        input_value = read_user_input()
        if input_value:  # Check if input is not empty
            execute(
                input_value, txt_folder_path, triple_folder_path, combined_file_path
            )
            # Delete folders after execute
            delete_folder(txt_folder_path)
            delete_folder(triple_folder_path)
        else:
            print("No URLs entered. Exiting.")
    except KeyboardInterrupt:
        print("\nUser interrupted. Exiting.")

