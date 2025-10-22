from backend import logic
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Python API läuft"}

@app.post("/test")
async def test(request: Request):
    data = await request.json()
    text = data.get("text")
    # Simulation: Verarbeitung
    return {"result": f"Analysiere: {text}"}

def match(string: str) -> bool:
    return logic.match(string)

# match regex pattern
# api/match
def build_regex(string: str) -> str:
    return logic.build_regex(string)

# build regex
# api/build
def detect_type_text(string: str, is_file: bool, is_ml: bool) -> str:
    return logic.detect_filetype(string, is_file, is_ml).name


def start_api():
    print("App läuft auf 127.0.0.1:50123")
    uvicorn.run(app, host="127.0.0.1", port=50123)

if __name__ == '__main__':
    start_api()
