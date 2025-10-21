import re
from .FileType import FileType as ft
import ml.transformer as transformer


def match(string: str) -> bool:
    if string is None:
        return False
    else:
        return re.match(string)

def build_regex(filetype: ft, string: str) -> str:
    pass

def detect_filetype(string: str) -> ft:
    pred, probs = transformer.predict(string)
    return ft[pred]