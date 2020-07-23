from enum import Enum


class Types(Enum):
    INT = -1
    FLOAT = -2


class Variable:
    def __init__(self, name, types: Types):
        self.name = name
        self.type = types
