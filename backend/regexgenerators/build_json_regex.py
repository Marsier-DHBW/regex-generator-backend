import json
import re
from re import Pattern


def json(string: str) -> Pattern[str]:
    regex_pattern = "^" + __build_json_regex_recursive(data=string) + "$"
    return re.compile(regex_pattern)

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
            return f'"[^"\\\\]*"'

    elif isinstance(data, dict):
        pattern_list = []
        for key, value in data.items():
            key_pattern = f'"{re.escape(key)}"\\s*:\\s*'
            value_pattern = __build_json_regex_recursive(value, depth + 1, max_depth)
            pattern_list.append(key_pattern + value_pattern)
        combined = "\\s*,\\s*".join(pattern_list)
        return f"\\{{\\s*{combined}\\s*\\}}"

    elif isinstance(data, list):
        inner_patterns = [__build_json_regex_recursive(v, depth + 1, max_depth) for v in data]
        combined = "\\s*,\\s*".join(inner_patterns)
        return f"\\[\\s*({combined})?\\s*\\]"

    elif isinstance(data, (int, float)):
        return r"-?\d+(\.\d+)?"

    elif isinstance(data, bool):
        return r"(true|false)"

    elif data is None:
        return "null"

    else:
        return f'"[^"\\\\]*"'
