from enum import Enum


class Types(Enum):
    INT = -1
    FLOAT = -2
    BOOL = -3

    @staticmethod
    def from_identifier(identifier):
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
