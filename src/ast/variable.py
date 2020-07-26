from enum import Enum


class Types(Enum):
    INT = -1
    FLOAT = -2
    BOOL = -3
    POINTER = -4

    __counter = 1
    custom_types = {}

    @staticmethod
    def nextTypeNumber():
        c = Types.__counter
        Types.__counter += 1
        return c

    @staticmethod
    def from_identifier(identifier: str):
        if identifier == "int":
            return Types.INT
        elif identifier == "double":
            return Types.FLOAT
        elif identifier == "bool":
            return Types.BOOL
        return None


class Variable:
    def __init__(self, name, types: Types):
        self.name = name
        self.type = types
