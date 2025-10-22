from backend import logic

# match regex pattern
# api/match
def match(string: str) -> bool:
    return logic.match(string)

# build regex from file
# api/build
def build_regex(string: str) -> str:
    return logic.build_regex(string)

# get file type from file
# api/detect
def detect_type_text(string: str, is_file: bool, is_ml: bool) -> str:
    return logic.detect_filetype(string, is_file, is_ml).name
