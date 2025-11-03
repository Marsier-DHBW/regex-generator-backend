from html.parser import HTMLParser
import re

class MyHTMLParser(HTMLParser):
    __regex_pattern: str = ''
    def handle_starttag(self, tag, attrs):
        regex_tag = fr'<{tag}\b[^>]*>\s*'
        print(f"Tag: {tag}")
        self.__regex_pattern = self.__regex_pattern + regex_tag

    def handle_endtag(self, tag):
        regex_tag = fr'<\/{tag}>\s*'
        print(f"Tag: {tag}")
        self.__regex_pattern = self.__regex_pattern + regex_tag

    def handle_data(self, data):
        data = data.strip()
        if len(data) == 0:
            return

        regex_tag = fr'[^<]*\s*'
        print(f"Data: {data}")
        self.__regex_pattern = self.__regex_pattern + regex_tag
    def get_regex(self):
        return '^' + self.__regex_pattern[:-3] + '$'

def html_pattern(string: str) -> re.Pattern[str]:
    parser = MyHTMLParser()
    try:
        parser.feed(string)
        return re.compile(parser.get_regex())
    except Exception as e:
        raise e