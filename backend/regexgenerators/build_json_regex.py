import json
import re
from re import Pattern


def json_pattern(string: str) -> Pattern[str]:
    try:
        regex_pattern = f'^{__build_json_regex_recursive(data=string)}$'
        return re.compile(regex_pattern)
    except Exception as ex:
        raise ex

def __build_json_regex_recursive(data, depth=0, max_depth=3):
    if depth > max_depth:
        raise ValueError("Maximale Tiefe überschritten")

        # Falls das Eingabedatum ein JSON-String ist, automatisch parsen
    if isinstance(data, str):
        try:
            parsed = json.loads(data)
            return __build_json_regex_recursive(parsed, depth, max_depth)
        except json.JSONDecodeError:
            # Wenn kein gültiges JSON, dann ist es ein reiner Textwert
            return r'"[^"\\]*"'

    elif isinstance(data, dict):
        pattern_list = []
        for key, value in data.items():
            key_pattern = fr'"{re.escape(key)}"\s*:\s*'
            value_pattern = __build_json_regex_recursive(value, depth + 1, max_depth)
            pattern_list.append(key_pattern + value_pattern)
        combined = r'\s*,\s*'.join(pattern_list)
        return fr'\{{\s*{combined}\s*\}}'

    elif isinstance(data, list):
        if len(data) == 0:
            return fr'\[\s*\]'
        else:
            inner_patterns = [__build_json_regex_recursive(v, depth + 1, max_depth) for v in data]
            longest_pattern = max(inner_patterns, key=len)
            return fr'\[\s*(({longest_pattern}\s*,\s*)*\s*({longest_pattern}\s*){{1}})?\s*\]'

    elif isinstance(data, bool):
        return r'(true|false)'

    elif isinstance(data, (int, float)):
        return r'-?\d+(\.\d+)?'

    elif data is None:
        return r'null'

    else:
        return fr'"[^"\\]*"'