from enum import Enum


class Token(Enum):
    EOF = -1
    EOL = -2
    FUN = -3
    EXTERN = -4
    IDENTIFIER = -5
    NUMBER = -6
    OPEN_PARENTH = -7
    CLOSE_PARENTH = -8
    COMMA = -9
    ADD = -10
    SUBTRACT = -11
    MULTIPLY = -12
    DIVIDE = -13
    END = -14
    RETURN = -15
    EQUALS = -16
    COLON = -17
    REF = -18
