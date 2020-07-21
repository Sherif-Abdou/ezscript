from enum import Enum


class Token(Enum):
    EOF = -1
    EOL = -2
    FUN = -3
    EXTERN = -4
    IDENTIFIER = -5
    NUMBER = -6
