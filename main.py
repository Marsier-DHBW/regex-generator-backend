from backend.filetype import FileType
from backend.regexgenerator import RegexGenerator

from backend.logic import build_regex

if __name__ == '__main__':
    print(build_regex(FileType.JSON, '{"name":"darian", "age": 5}'))
