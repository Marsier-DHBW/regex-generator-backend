from enum import Enum

# class syntax
class FileType(Enum):
    JSON = 0
    XML = 1
    CSV = 2
    HTML = 3
    UNSUPPORTED = 4