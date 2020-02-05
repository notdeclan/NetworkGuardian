class AbstractPlugin:

    def __init__(self, name, lol):
        self.lol = lol
        self.name = name

    def process(self):
        pass
