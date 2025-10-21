import re
import ml.transformer as transformer
from .filetype import FileType as ft
from .regexgenerator import RegexGenerator


def match(pattern: str, string: str) -> bool:
    if string is None:
        return False
    else:
        return bool(re.match(pattern=pattern, string=string))


def build_regex(filetype: ft, string: str) -> str:
    regex: str
    match filetype:
        case ft.JSON:
            regex = RegexGenerator.json(string)
        case ft.XML:
            regex = RegexGenerator.xml(string)
        case ft.HTML:
            regex = RegexGenerator.html(string)
        case ft.CSV:
            regex = RegexGenerator.csv(string)
        case _:
            regex = 'Unknown'
    return regex


def detect_filetype(string: str, is_file: bool, is_ml: bool) -> type(ft):
    filetype: type(ft) = ft.UNSUPPORTED
    if is_file:
        pass
        # easy logic
    else:
        if is_ml:
            pred, probs = transformer.predict(string)
            filetype = ft[pred]
        else:
            pass
            # Flo logic

    return filetype
