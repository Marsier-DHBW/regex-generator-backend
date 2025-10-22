import json
import re
from re import Pattern
from xml.etree import ElementTree
from itertools import groupby

class RegexGenerator:
    @staticmethod
    def json(string: str) -> Pattern[str]:
        regex_pattern = "^" + build_json_regex_recursive(data=string) + "$"
        return re.compile(regex_pattern)

    @staticmethod
    def csv(string: str) -> Pattern[str]:
        return "csv"

    @staticmethod
    def xml(string: str) -> Pattern[str]:
        regex_pattern = "^" + _generate_xml_regex(xml_string=string) + "$"
        return re.compile(regex_pattern)

    @staticmethod
    def html(string: str) -> Pattern[str]:
        return "html"


def build_json_regex_recursive(data, depth=0, max_depth=3):
    if depth > max_depth:
        raise ValueError("Maximale Tiefe überschritten")

        # Falls das Eingabedatum ein JSON-String ist, automatisch parsen
    if isinstance(data, str):
        try:
            parsed = json.loads(data)
            return build_json_regex_recursive(parsed, depth, max_depth)
        except json.JSONDecodeError:
            # Wenn kein gültiges JSON, dann ist es ein reiner Textwert
            return f'"[^"\\\\]*"'

    elif isinstance(data, dict):
        pattern_list = []
        for key, value in data.items():
            key_pattern = f'"{re.escape(key)}"\\s*:\\s*'
            value_pattern = build_json_regex_recursive(value, depth + 1, max_depth)
            pattern_list.append(key_pattern + value_pattern)
        combined = "\\s*,\\s*".join(pattern_list)
        return f"\\{{\\s*{combined}\\s*\\}}"

    elif isinstance(data, list):
        inner_patterns = [build_json_regex_recursive(v, depth + 1, max_depth) for v in data]
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

def _generate_xml_regex(xml_string: str, max_depth: int = 3) -> str:
    root = ElementTree.fromstring(xml_string)
    # Wir starten hier mit depth=1 für den Root-Tag
    pattern = _build_xml_regex_recursive(root, depth=1, max_depth=max_depth)
    return f"(?s){pattern}"


def _build_xml_regex_recursive(element: ElementTree.Element, depth: int, max_depth: int) -> str:
    tag = re.escape(element.tag)

    open_tag = f"<\\s*{tag}[^>]*>"
    close_tag = f"<\\s*/\\s*{tag}\\s*>"
    if depth > max_depth or len(element) == 0:
        content_pattern = "[^<]*"
    else:
        child_patterns = []
        for child in element:
            child_patterns.append(_build_xml_regex_recursive(child, depth + 1, max_depth))
        content_pattern = "\\s*".join(child_patterns)

    return f"{open_tag}\\s*{content_pattern}\\s*{close_tag}"