from enum import Enum


class ExpressionType(Enum):
    ADD = -1
    MINUS = -2
    MULTIPLY = -3
    DIVIDE = -4
    VALUE = -5
    REFERENCE = -6
    DEREFERENCE = -7
    PLACEHOLDER = -8


class Value:
    def __init__(self, value, te: ExpressionType):
        self.type = te
        self.right = None
        self.left = None
        self.value = value
