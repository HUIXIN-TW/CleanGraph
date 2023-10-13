from fastapi import FastAPI
from fastapi import APIRouter, HTTPException, Body
import subprocess
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Create a FastAPI instance
app = FastAPI()

# Set up CORS middleware to allow requests from all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

router = APIRouter(prefix="/crawler", tags=["crawler"])

class InputData(BaseModel):
    inputValue: str

@router.post("/run-script")
async def run_script(data: InputData):
    print(f"Running script with input value: {data.inputValue}")
    try:
        subprocess.run(['python3', '../test_script.py', data.inputValue], check=True, capture_output=True, text=True)
        return {"message": "Script executed successfully!"}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error executing script: {e.stdout} {e.stderr}")

# curl -X POST -H "Content-Type: application/json" -d '{"inputValue":"your_test_value_here"}' http://localhost:8000/crawler/run-script
# {"message":"Script executed successfully!"}%  