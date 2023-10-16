from bs4 import BeautifulSoup, NavigableString, Tag

import requests
import re
import os


def crawl_until_end(element) -> list:
    # If the element is a NavigableString (text), return it
    if isinstance(element, NavigableString):
        return [str(element)]

    # If the element is a Tag, recursively process its children
    if isinstance(element, Tag):
        return [
            child_str
            for child in element.contents
            for child_str in crawl_until_end(child)
        ]

    return []


def generateTxt(url):
    output_directory = "crawler_results/"
    create_directory(output_directory)

    unit_code = extract_unit_code(url)
    file_path = os.path.join(output_directory, f"unit_{unit_code}.txt")

    try:
        source = fetch_web_content(url)
        soup = BeautifulSoup(source.content, "html5lib")

        with open(file_path, "w", encoding="utf-8") as f:
            write_content_to_file(soup, f)

        print("Text crawled for unit details")

    except Exception as e:
        print(f"Error processing URL {url}: {e}")


def create_directory(directory_path: str) -> None:
    """Creates the directory if it doesn't exist."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def extract_unit_code(url: str) -> str:
    """Extracts the unit code from the URL."""
    return url.split("=")[-1]


def fetch_web_content(url: str) -> requests.models.Response:
    """Fetches the content of the web page."""
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    return response


def write_content_to_file(soup: BeautifulSoup, file) -> None:
    """Writes the extracted content to the specified file."""
    title = soup.find("h2", attrs={"id": "pagetitle"})
    details_list = soup.find("dl", attrs={"class": "ruled"})
    dt_elements = details_list.find_all("dt")
    dd_elements = details_list.find_all("dd")

    # write title to the file
    file.write(title.text + "\n")

    for dt_e, dd_e in zip(dt_elements, dd_elements):
        file.write(dt_e.get_text() + ":")
        all_elements = crawl_until_end(dd_e)
        for el in all_elements:
            stripped_item = el.strip()
            if stripped_item:
                file.write(el)
        file.write("\n")


if __name__ == "__main__":
    url = "https://handbooks.uwa.edu.au/unitdetails?code=CITS1003"
    generateTxt(url)
