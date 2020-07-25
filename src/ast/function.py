from .scope import Scope


class Function(Scope):
    def __init__(self, name, args=None):
        super().__init__()
        if args is None:
            args = []
        else:
            self.variables += args
        self.name = name
        self.args = args
