import re
import os
from .FileType import FileType as ft
import ml.transformer as transformer


def match(string: str) -> bool:
    if string is None:
        return False
    else:
        return re.match(string)

def build_regex(filetype: ft, string: str) -> str:
    pass

def detect_filetype(string: str, is_file: bool, is_ml: bool) -> ft:
    if is_file:
        pass
        # easy logic
    else:
        if is_ml:
            pred, probs = transformer.predict(string)
        else:
            pass
            # Flo logic

    return None