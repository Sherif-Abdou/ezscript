from typing import List

from .variable import Variable
import src.ast as ast


class Scope:
    def __init__(self, root=False):
        self.commands = []
        self.variables: List[Variable] = []
        self.functions: List[ast.Function] = []
        self.root = root
