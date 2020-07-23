class Scope:
    def __init__(self, root=False):
        self.commands = []
        self.variables = []
        self.functions = []
        self.root = root
