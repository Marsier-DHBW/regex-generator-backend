import ml.transformer as t
from backend.filetype import FileType
from backend.logic import build_regex
from backend.Regexgenerator import RegexGenerator

if __name__ == '__main__':
    print(build_regex(FileType.JSON, '{"name":"darian", "age": 5}'))

