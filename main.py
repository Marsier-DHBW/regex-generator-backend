import re
from backend import logic
from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()
api_endpoint = "/v1/api/endpoint"

@app.get(api_endpoint)
async def root():
    return {"message": "Python API läuft"}

@app.post(api_endpoint + "/match")
async def match(request: Request):
    request_body = await request.json()
    string = request_body.get("text")
    regex = request_body.get("regex")
    if regex is None or len(regex) == 0:
        regex_pattern = None
    else:
        regex_pattern = re.compile(regex)

    result_obj = {"value": False, "message": ""}

    if regex_pattern is None or string is None or len(string) == 0:
        result_obj["message"] = "Either the pattern or the string was null"
        return JSONResponse(content=result_obj, status_code=status.HTTP_400_BAD_REQUEST)

    result_obj["value"] = logic.match(regex_pattern, string)
    result_obj["message"] = "Successfully matched the pattern"
    return JSONResponse(content=result_obj, status_code=status.HTTP_200_OK)



def build_regex(string: str) -> str:

    return logic.build_regex(string)

def detect_type_text(string: str, is_file: bool, is_ml: bool) -> str:
    return logic.detect_filetype(string, is_file, is_ml).name


def start_api():
    print("App läuft auf 127.0.0.1:50123")
    uvicorn.run(app, host="127.0.0.1", port=50123)

if __name__ == '__main__':
    start_api()
