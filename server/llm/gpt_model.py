import os
import openai
import json
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)


class GPTModel:
    def __init__(self, model_name: str, file_path: str, initial_prompt_chunk_path: str):
        """
        Initialize the GPTModel class.
        Set the model name and the default file path.
        """
        self._load_env_variables()
        self.model_name = model_name
        self.default_file_path = file_path
        self.initial_prompt_chunk = initial_prompt_chunk_path
        logging.info(f"Model: Set to {model_name} with chuncked triplets")

    def _load_env_variables(self):
        """
        Helper Method: Load the environment variables from the .env file.
        Exit if the OPENAI_API_KEY is not set.
        """
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logging.error("API_KEY not found. Please set it in the .env file.")
            exit(1)
        openai.api_key = api_key

    def _get_file_name(self) -> str:
        """
        Helper Method: Get the file name from the user input.
        Return the full path as a string.
        """
        # while True:
        #     choosen_file = input(
        #         f"Which file do you want to use under {self.default_file_path}? "
        #     )
        #     if choosen_file:
        #         return f"{self.default_file_path}{choosen_file}"
        #     print("Please enter a valid file name")
        return f"{self.default_file_path}"

    def _read_from_file(self, filename: str) -> str:
        """
        Helper Method: Read content from a file
        Rreturn the content as a string.
        """
        return Path(filename).read_text(encoding="utf-8")

    def _generate_filename(self, prompt_name: str) -> str:
        """
        Helper Method: Generate a filename based on the current datetime.
        Return the filename as a string.
        """
        current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"triple_results/{prompt_name}-output-{current_time}.json"

    def _save_to_file(self, content: str, filename: str) -> str:
        """
        Helper Method: Save the provided content to a file.
        Return the filename as a string.
        """
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(content, indent=2))
        return filename

    def _parse_chunked_result(self, chunked_result):
        """
        Helper Method: Parse the chunked result into a list of triplets.
        Return the combined results as a list.
        """
        combined_results = []
        try:
            chunked_result_list = chunked_result.split("\n\n")
        except Exception as e:
            logging.error(f"Failed to split chunked result into list. {e}")
            return combined_results

        for chunk in chunked_result_list:
            try:
                json_object = json.loads(chunk)
                if isinstance(json_object, list):
                    for item in json_object:
                        if all(
                            key in item
                            for key in ("head", "head_type", "tail", "tail_type")
                        ):
                            combined_results.append(item)
                else:
                    if all(
                        key in json_object
                        for key in ("head", "head_type", "tail", "tail_type")
                    ):
                        combined_results.append(json_object)
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON chunk: {chunk}. Error: {e}")
        return combined_results

    def get_triplets_chunk(self, user_message: str, chunk_size: int = 1) -> str:
        """
        Get triplets from a given user message in chunks.
        Return the chunked results as a string.
        """
        paragraphs = user_message.split("\n\n")
        chunks = self._chunk_paragraphs(paragraphs, chunk_size)
        return self._get_chunk_responses(chunks)

    def _chunk_paragraphs(self, paragraphs: list, chunk_size: int) -> list:
        """
        Hepler Method: Split paragraphs into chunks based on the chunk size.
        Return the chunks as a list.
        """
        chunks, current_chunk, current_length = [], [], 0
        for para in paragraphs:
            if current_length + len(para.split()) <= chunk_size:
                current_chunk.append(para)
                current_length += len(para.split())
            else:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [para]
                current_length = len(para.split())
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
        return chunks

    def _get_chunk_responses(self, chunks: list) -> str:
        """
        Helper Method: Get responses for each chunk from the API.
        Return the chunked results as a string.
        """
        all_results = []
        for chunk in chunks:
            logging.info(
                f"Processing Chunk: {chunk[:30]}..."
            )  # Logging first 30 characters of the chunk
            completion = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.initial_prompt_chunk},
                    {"role": "user", "content": chunk},
                ],
                temperature=0.2,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            )
            all_results.append(completion.choices[0].message["content"])
        return "\n\n".join(all_results)

    def main(self):
        input_file = self._read_from_file(self._get_file_name())
        print(f"Get file content from {self._get_file_name()}")
        chunked_result = self.get_triplets_chunk(input_file)
        combined_results = self._parse_chunked_result(chunked_result)

        print(json.dumps(combined_results, indent=2))

        output_file = self._generate_filename("gpt-3.5-turb-chunk")
        chunked_result_file_name = self._save_to_file(combined_results, output_file)

        print(f"Saved chunked results to {chunked_result_file_name}")

        # kg = KnowledgeGraph(output_file)
        # visualization_file = kg.visualize()

        # print(f"Knowledge graph visualization saved as {visualization_file}.")


if __name__ == "__main__":
    model_name = "ft:gpt-3.5-turbo-0613:uwa-csse:uwa-dataset:84kffWR6"
    file_path = "txt_results/MIT.txt"
    initial_prompt_chunk_path = "initial_prompts.txt"
    gpt = GPTModel(model_name, file_path, initial_prompt_chunk_path)
    gpt.main()
