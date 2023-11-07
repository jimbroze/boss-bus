class NoDeps:
    def __init__(self) -> None:
        self.output = "No dependencies loaded"


class SimpleDeps:
    def __init__(self, dep_one: NoDeps, dep_two: NoDeps):
        self.dep_one = dep_one
        self.dep_two = dep_two
        self.output = "One dependency loaded"


class LayeredDeps:
    def __init__(self, dep_one: SimpleDeps, dep_two: NoDeps):
        self.dep_one = dep_one
        self.dep_two = dep_two
        self.output = "Layered dependencies loaded"


class CustomDeps:
    def __init__(self, dep_one: str, dep_two: SimpleDeps):
        self.dep_one = dep_one
        self.dep_two = dep_two
        self.output = self.dep_one
