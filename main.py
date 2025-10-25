import re
import os
import ml.transformer
from backend import logic
from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
import uvicorn
from backend.enums.FileType import FileType

app = FastAPI()

url = str(os.environ.get("URL"))
port = int(os.environ.get("PORT"))
api_endpoint = str(os.environ.get("ENDPOINT"))

@app.get(api_endpoint)
async def root():
    return {"message": "Python API läuft"}

@app.post(api_endpoint + "/match")
async def match(request: Request) -> JSONResponse:
    request_body = await request.json()
    string = request_body.get("text")
    regex = request_body.get("regex")
    if regex is None or len(regex) == 0:
        regex_pattern = None
    else:
        regex_pattern = re.compile(regex)

    result_obj = {"value": False, "message": ""}

    if regex_pattern is None or string is None or len(string) == 0:
        result_obj["message"] = "Error. Either the regex or the text was null"
        return JSONResponse(content=result_obj, status_code=status.HTTP_400_BAD_REQUEST)

    result_obj["value"] = logic.match(regex_pattern, string)
    result_obj["message"] = "Successfully matched the pattern"
    return JSONResponse(content=result_obj, status_code=status.HTTP_200_OK)


@app.post(api_endpoint + "/generate")
async def generate_regex(request: Request) -> JSONResponse:
    request_body = await request.json()
    string = request_body.get("text")
    filetype = request_body.get("filetype")
    ft = FileType.UNSUPPORTED
    result_obj = {"value": "", "message": ""}

    if string is None or len(string) == 0 or filetype is None or len(filetype) == 0:
        result_obj["message"] = "Error. Either the text or the filetype was null"
        return JSONResponse(content=result_obj, status_code=status.HTTP_400_BAD_REQUEST)
    elif filetype is not None and len(filetype) > 0:
        bad_type = False
        try:
            ft = FileType[filetype]
            bad_type = ft == FileType.UNSUPPORTED
        except Exception:
            bad_type = True

        if bad_type:
            result_obj["message"] = "Error. File type is not supported"
            return JSONResponse(content=result_obj, status_code=status.HTTP_400_BAD_REQUEST)

    try:
        result = logic.generate_regex(filetype=ft, string=string)
        result_obj["value"] = result
        result_obj["message"] = "Successfully generated regex pattern"
        return JSONResponse(content=result_obj, status_code=status.HTTP_200_OK)
    except Exception as e:
        result_obj["message"] = f"Error. Message: {str(e)}"
        return JSONResponse(content=result_obj, status_code=status.HTTP_400_BAD_REQUEST)

@app.post(api_endpoint + "/detectfiletype")
async def detect_type_text(request: Request) -> JSONResponse:
    request_body = await request.json()
    string = request_body.get("text")
    is_ml = request_body.get("ml")
    result_obj = {"value": "", "message": ""}

    if string is None or len(string) == 0 or is_ml is None or type(is_ml) is not bool:
        result_obj["message"] = "Error. Either the text or ml is null/not a boolean"
        return JSONResponse(content=result_obj, status_code=status.HTTP_400_BAD_REQUEST)

    probs: dict
    try:
        probs = logic.detect_filetype(string=string, is_ml=bool(is_ml))
    except Exception as e:
        result_obj["message"] = f"Error. Message: {str(e)}"
        return JSONResponse(content=result_obj, status_code=status.HTTP_400_BAD_REQUEST)

    result_obj["message"] = "Successfully detected file type"
    result_obj["value"] = probs
    return JSONResponse(content=result_obj, status_code=status.HTTP_200_OK)

def start_api():
    print(f"App läuft auf {url}:{port}")
    uvicorn.run(app, host=url, port=port)

if __name__ == '__main__':
    ml.transformer.prepare_model()
    print(f"Testing with string: \"<root></root>\": {str(ml.transformer.predict("<root></root>"))}")
    start_api()
