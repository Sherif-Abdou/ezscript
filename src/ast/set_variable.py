class SetVariable:
    def __init__(self, name, value, deref=False):
        self.name = name
        self.value = value
        self.deref = deref
