import os
import requests
from bs4 import BeautifulSoup


def extract_course_info(url):
    try:
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            course_name_tag = soup.find("h2", id="pagetitle")
            course_code = url.split("=")[-1]
            if course_name_tag:
                course_name = course_name_tag.get_text(strip=True)
            else:
                course_name = f"Course Name Not Found [{course_code}]"

            # Find the "Course overview" section
            course_overview_tag = soup.find("h3", string="Course overview")
            if course_overview_tag:
                course_overview_dl = course_overview_tag.find_next(
                    "dl", class_="columns ruled"
                )
                course_overview = {}
                for dt, dd in zip(
                    course_overview_dl.find_all("dt"), course_overview_dl.find_all("dd")
                ):
                    course_overview[dt.get_text(strip=True)] = dd.get_text(strip=True)
            else:
                course_overview = {"Course overview": "Not Found"}

            # Find the "Course details" section
            course_details_tag = soup.find("h3", string="Course details")
            if course_details_tag:
                course_details_dl = course_details_tag.find_next(
                    "dl", class_="columns ruled"
                )
                course_details = {}
                for dt, dd in zip(
                    course_details_dl.find_all("dt"), course_details_dl.find_all("dd")
                ):
                    course_details[dt.get_text(strip=True)] = dd.get_text(strip=True)
            else:
                course_details = {"Course details": "Not Found"}

            # Locate the main sequencer div
            sequencer_div = soup.find("div", class_="sequencer")

            if sequencer_div:
                # Initialize lists to store titles and tables
                titles = []
                tables = []

                # Extract all titles and tables within the sequencer div
                for child in sequencer_div.children:
                    if child.name == "p" and child.get("class") == ["Regulation"]:
                        titles.append(child.get_text(strip=True))
                    elif child.name == "div" and child.get("class") == ["table-scroll"]:
                        tables.append(child.find("table", class_="styled width-max"))

                # Process each title-table pair
                course_structure = []
                for title, table in zip(titles, tables):
                    if table:
                        headers = [
                            th.get_text(strip=True) for th in table.find_all("th")
                        ]
                        unit_info_list = []
                        for row in table.find_all("tr")[1:]:
                            cols = row.find_all("td")
                            unit_info = {}
                            for header, col in zip(headers, cols):
                                unit_info[header] = col.get_text(strip=True)
                            unit_info_list.append(unit_info)
                        course_structure.append(
                            {"title": title, "units": unit_info_list}
                        )
                    else:
                        course_structure.append(
                            {
                                "title": title,
                                "units": [{"Course structure": "Table Not Found"}],
                            }
                        )

            else:
                print("Sequencer div not found!")

            formatted_info = f"Course overview of {course_name}\n"
            for key, value in course_overview.items():
                formatted_info += f"{key.strip()}: {value.strip()}\n"

            for key, value in course_details.items():
                formatted_info += f"{key.strip()}: {value.strip()}\n"

            for section in course_structure:
                formatted_info += f"\nCourse Structure of {course_name}"
                formatted_info += f"\n{section['title']}\n"
                for unit_info in section["units"]:
                    for key, value in unit_info.items():
                        formatted_info += f"{key.strip()}: {value.strip()}\n"
        else:
            print(f"Failed to fetch URL: {url}, Status Code: {response.status_code}")

    except Exception as e:
        print(f"Error occurred while processing URL: {url}, Error: {str(e)}")

    return formatted_info


def generateTxt(url):
    # Create an output directory to store all files
    output_directory = "crawler_results/"

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    course_info = extract_course_info(url)
    if course_info:
        # Extract the degree code from the URL
        degree_code = url.split("=")[-1]
        file_name = f"degree_{degree_code}.txt"
        file_path = os.path.join(output_directory, file_name)

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(course_info)
        except Exception as e:
            print(f"Error occurred while saving file: {file_path}, Error: {str(e)}")

        print(f"Information extracted from {url} and saved to {file_path}")
        return file_path


if __name__ == "__main__":
    url = "https://handbooks.uwa.edu.au/coursedetails?code=62510"
    generateTxt(url)
