from boss_bus.loader.instantiator import ClassInstantiator


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


class TestClassInstantiator:
    def test_load_returns_instance_if_provided(self) -> None:
        loader = ClassInstantiator()
        instance = NoDeps()

        loaded_class = loader.load(instance)
        assert isinstance(loaded_class, NoDeps)
        assert loaded_class.output == "No dependencies loaded"

    def test_load_instantiates_class_with_no_dependencies(self) -> None:
        loader = ClassInstantiator()

        loaded_class = loader.load(NoDeps)
        assert isinstance(loaded_class, NoDeps)
        assert loaded_class.output == "No dependencies loaded"

    def test_load_instantiates_class_with_one_layer_of_simple_dependencies(
        self,
    ) -> None:
        loader = ClassInstantiator()

        loaded_class = loader.load(SimpleDeps)
        assert isinstance(loaded_class, SimpleDeps)
        assert loaded_class.output == "One dependency loaded"

    def test_load_instantiates_class_with_multiple_layers_of_simple_dependencies(
        self,
    ) -> None:
        loader = ClassInstantiator()

        loaded_class = loader.load(LayeredDeps)
        assert isinstance(loaded_class, LayeredDeps)
        assert loaded_class.output == "Layered dependencies loaded"
        assert loaded_class.dep_one.output == "One dependency loaded"
