from fastapi import APIRouter, HTTPException, Body
import subprocess
from pydantic import BaseModel

router = APIRouter(prefix="/crawler", tags=["crawler"])

class InputData(BaseModel):
    inputValue: str

@router.post("/run-script")
async def run_script(data: InputData):
    print(f"Running script with input value: {data.inputValue}")
    try:
        result = subprocess.run(['python3', '../test_script.py', data.inputValue], check=True, capture_output=True, text=True)
        print("Script Output:", result.stdout)
        print("Script Errors:", result.stderr)
        return {"message": "Script executed successfully!"}
    except subprocess.CalledProcessError as e:
        print("Error Output:", e.stdout)
        print("Error Errors:", e.stderr)
        raise HTTPException(status_code=500, detail=f"Error executing script: {e.stdout} {e.stderr}")

# curl -X POST -H "Content-Type: application/json" -d '{"inputValue":"your_test_value_here"}' http://localhost:8000/crawler/run-script
# {"message":"Script executed successfully!"}%  