import re
from re import Pattern
from xml.etree import ElementTree
from typing import Optional

def xml_pattern(string: str) -> Optional[Pattern[str]]:
    try:
        root = ElementTree.fromstring(string)
        pattern = re.compile(__build_xml_regex_recursive(element=root, depth=1, max_depth=3))
        return pattern
    except ElementTree.ParseError:
        print("Fehler beim parsing des XML")
        return None

def __build_xml_regex_recursive(element: ElementTree.Element, depth: int, max_depth: int) -> str:
    tag = re.escape(element.tag)
    open_tag = f"<\\s*{tag}[^>]*>"
    close_tag = f"<\\s*/\\s*{tag}\\s*>"
    if depth > max_depth or len(element) == 0:
        content_pattern = "[^<]*"
    else:
        child_patterns = []
        for child in element:
            child_patterns.append(__build_xml_regex_recursive(child, depth + 1, max_depth))
        content_pattern = "\\s*".join(child_patterns)

    return f"{open_tag}\\s*{content_pattern}\\s*{close_tag}"