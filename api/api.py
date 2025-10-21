from backend import logic


# match regex pattern
def match(string: str) -> bool:
    return logic.match(string)

# build regex from file
def build_regex(string: str) -> str:
    return logic.build_regex(string)

# get file type from file
def detect_type(string: str) -> str:
    return logic.detect_filetype(string).name
