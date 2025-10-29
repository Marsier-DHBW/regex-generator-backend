import re
import unittest
from re import Pattern
from xml.etree import ElementTree
from typing import Optional

def xml_pattern(string: str) -> Optional[Pattern[str]]:
    try:
        root = ElementTree.fromstring(string)
        pattern_string = __build_xml_regex_recursive(element=root, depth=1, max_depth=3)
        pattern = re.compile(fr"(?s){pattern_string}")
        return pattern
    except ElementTree.ParseError:
        print("Fehler beim parsing des XML")
        return None

def __build_xml_regex_recursive(element: ElementTree.Element, depth: int, max_depth: int) -> str:
    tag = re.escape(element.tag)
    open_tag = fr"<\s*{tag}\b[^>]*>"
    close_tag = fr"<\s*/\s*{tag}\s*>"
    if depth >= max_depth:
        content_pattern = r".*?"
    elif len(element) == 0:
        content_pattern = r"[^<]*"
    else:
        child_patterns = []
        for child in element:
            child_patterns.append(__build_xml_regex_recursive(child, depth + 1, max_depth))
        content_pattern = fr"\s*".join(child_patterns)

    return fr"{open_tag}\s*{content_pattern}\s*{close_tag}"