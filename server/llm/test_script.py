import sys

# Check if an argument was provided
if len(sys.argv) > 1:
    input_value = sys.argv[1]
else:
    input_value = "No input value provided."

print(input_value)

# Create a txt file with the provided input value
with open("../tmp/output.txt", "w") as file:
    file.write(input_value)


# Entire /src/ Folder put int /llm/ folder here (TBC)
# import Crawler
# import GPTmodel

# Step 0: Get the input from the user
# Step 1: Run the crawler, then generate a .txt file under tmp
# Step 2: Run GPT model, then generate a userdata.js file under client/src/shared/userdata.js
# Step 3: Clear the tmp folder
