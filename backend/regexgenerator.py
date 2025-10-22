import re
from re import Pattern
from regexgenerators.build_json_regex import build_json_regex_recursive
from backend.regexgenerators.build_csv_regex import build_csv_regex

class RegexGenerator:
    @staticmethod
    def json(string: str) -> Pattern[str]:
        regex_pattern = "^" + build_json_regex_recursive(data=string) + "$"
        return re.compile(regex_pattern)

    @staticmethod
    def csv(string: str) -> Pattern[str]:
        regex_pattern = build_csv_regex(string)
        return re.compile(regex_pattern)

    @staticmethod
    def xml(string: str) -> Pattern[str]:
        return "xml"

    @staticmethod
    def html(string: str) -> Pattern[str]:
        return "html"
