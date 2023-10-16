from fastapi import FastAPI, APIRouter, HTTPException, Body
from pydantic import BaseModel

import sys
sys.path.append('..')

from llm import run_script

# Create a FastAPI instance
app = FastAPI()

router = APIRouter(prefix="/crawler", tags=["crawler"])

class InputData(BaseModel):
    inputValue: str

@router.post("/run-script")
async def run_script_endpoint(data: InputData):
    print(f"Running script with input value: {data.inputValue}")
    try:
        # Call the function directly
        txt_folder_path = "crawler_results"
        triple_folder_path = "triple_results"
        combined_file_path = "../client/src/shared/userdata.js"
        run_script.execute(data.inputValue, txt_folder_path, triple_folder_path, combined_file_path)
        return {"message": "Script executed successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(router)
