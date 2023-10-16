import os
import sys
import json
import shutil
from pathlib import Path
from . import gpt_model
from . import crawler_degree
from . import crawler_unit
# import gpt_model
# import crawler_degree
# import crawler_unit


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
    
    initial_prompt_chunk_path = """You are a triple extract assistant specialized in analyzing university degrees and course details. Given a prompt that contains information about a university degree or course, your task is to extrapolate as many relationships as possible, paying particular attention to the "Description: ", "Outcomes: " and "Assessment: " sections, if available.
Create a JSON output comprising triplets that adhere to the following format: [{"head": "Entity1", "head_type": "Type1", "relation": "Relationship", "tail": "Entity2", "tail_type": "Type2"},  ... (more triplets)]
In this format:
"head" represents the first entity (Entity1) involved in the relationship.
"head_type" denotes the category or classification of Entity1 (e.g., "Course", "Skill", "Topic", "Assessment", "Unit", "Activity", "Outcome", "Unit Coordinator" etc.).
"relation" is a verb phrase that describes the relationship between Entity1 and Entity2. This relationship is directed, implying that the order of entities matters.
"tail" stands for the second entity (Entity2) involved in the relationship.
"tail_type" signifies the category or classification of Entity2 (e.g., "Course", "Skill", "Topic", "Assessment", "Unit", "Activity", "Outcome", "Unit Coordinator" etc.).

In the context of tracking student outcomes for a specific unit, it's advisable to introduce a 'student' entity between the 'unit' and 'outcome'. This will provide a clearer representation of each student's performance in that unit.
Outcomes: Students are able to (1) describe the concepts of cybersecurity and information security as made up by the different domains of knowledge in the unit outline; (2) specify the role of cybersecurity risk management in an overall strategy of providing information security by applying mitigations in the different cybersecurity domains; and (3) define the legal and ethical responsibilities of a cybersecurity professional.
"[{"head": "CITS1003 Introduction to Cybersecurity", "head_type": "Unit", "relation": "enables", "tail": "CITS1003 Student", "tail_type": "Student"}, {"head": "CITS1003 Student", "head_type": "Student", "relation": "describes", "tail": "concepts of cybersecurity and information security", "tail_type": "Concept"}, {"head": "concepts of cybersecurity and information security", "head_type": "Concept", "relation": "comprises", "tail": "different domains of knowledge in the unit outline", "tail_type": "Content Source"}, {"head": "CITS1003 Student", "head_type": "Student", "relation": "specify", "tail": "role of cybersecurity risk management", "tail_type": "Concept"}, {"head": "role of cybersecurity risk management", "head_type": "Concept", "relation": "used for", "tail": "providing information security", "tail_type": "Strategy"}, {"head": "providing information security", "head_type": "Strategy", "relation": "applies", "tail": "mitigations in cybersecurity domains", "tail_type": "Method"},{"head": "CITS1003 Student", "head_type": "Student", "relation": "defines", "tail": "legal and ethical responsibilities of a cybersecurity professional", "tail_type": "Concept"}]"

In the context of unit assessments, it's essential to introduce an 'assessment' entity between the 'unit' and 'assessment details'. This will offer a structured way to link specific units with their respective assessment details.
Assessment: Indicative assessments in this unit are as follows: (1) laboratory with quizzes; (2) project; and (3) final examination. Further information is available in the unit outline. Students may be offered supplementary assessment in this unit if they meet the eligibility criteria.
[{"head": "CITS1003 Introduction to Cybersecurity", "head_type": "Unit", "relation": "has", "tail": "CITS1003 Assessment", "tail_type": "Assessment"}, {"head": "CITS1003 Assessment", "head_type": "Assessment", "relation": "includes", "tail": "laboratory with quizzes", "tail_type": "Quize"}, {"head": "CITS1003 Assessment", "head_type": "Assessment", "relation": "includes", "tail": "project", "tail_type": "Project"}, {"head": "CITS1003 Assessment", "head_type": "Assessment", "relation": "includes", "tail": "final examination", "tail_type": "final examination"}, {"head": "CITS1003 Assessment", "head_type": "Assessment", "relation": "may offers", "tail": "supplementary assessment", "tail_type": "Supplementary assessment"}]
  
Your task is to identify and represent as many meaningful relationships as possible from the provided information. Optimize your graph's depth to fully leverage its potential and capture intricate patterns in the data. Remember to keep the output neat and well-organized."""


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


def write_to_json(triples: list, output_path: str) -> None:
    """Writes a list to a JSON file."""
    try:
        filtered_triples = []
        removed_triples = []
        # Filter out triples with any 'null' value
        for triple in triples:
            if all(value is not None for value in triple.values()):
                filtered_triples.append(triple)
            else:
                removed_triples.append(triple)
        print("\nRemoved triples:")
        print(removed_triples)

        with open(output_path, "w") as outfile:
            outfile.write(f'export const UserData = {filtered_triples};')

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

    triple_results_folder_path = 'triple_results'
    if not os.path.exists(triple_results_folder_path):
        os.makedirs(triple_results_folder_path)

    crawler_results_folder_path = 'crawler_results'
    if not os.path.exists(crawler_results_folder_path):
        os.makedirs(crawler_results_folder_path)

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
        # Delete folders after execute
        delete_folder(txt_folder_path)
        delete_folder(triple_folder_path)
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
    combined_file_path = "../client/src/shared/userdata.js"

    try:
        # input_value = input("Enter one or more space-separated URLs to process:\n")
        input_value = read_user_input()
        if input_value:  # Check if input is not empty
            execute(
                input_value, txt_folder_path, triple_folder_path, combined_file_path
            )
        else:
            print("No URLs entered. Exiting.")
    except KeyboardInterrupt:
        print("\nUser interrupted. Exiting.")

