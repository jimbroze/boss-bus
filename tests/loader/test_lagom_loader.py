from lagom import Container

from boss_bus.loader.lagom_loader import LagomLoader


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


class TestClassInstantiator:
    def test_lagom_load_returns_instance_if_provided(self) -> None:
        loader = LagomLoader()
        instance = NoDeps()

        loaded_class = loader.load(instance)
        assert isinstance(loaded_class, NoDeps)
        assert loaded_class.output == "No dependencies loaded"

    def test_lagom_load_instantiates_class_with_no_dependencies(self) -> None:
        loader = LagomLoader()

        loaded_class = loader.load(NoDeps)
        assert isinstance(loaded_class, NoDeps)
        assert loaded_class.output == "No dependencies loaded"

    def test_lagom_load_instantiates_class_with_multiple_layers_of_simple_dependencies(
        self,
    ) -> None:
        loader = LagomLoader()

        loaded_class = loader.load(LayeredDeps)
        assert isinstance(loaded_class, LayeredDeps)
        assert loaded_class.output == "Layered dependencies loaded"
        assert loaded_class.dep_one.output == "One dependency loaded"

    def test_lagom_load_accepts_a_custom_container(
        self,
    ) -> None:
        loader = LagomLoader(Container())

        loaded_class = loader.load(LayeredDeps)
        assert isinstance(loaded_class, LayeredDeps)

    def test_lagom_load_resolves_complex_types(
        self,
    ) -> None:
        container = Container()
        container[CustomDeps] = lambda simple_dep: CustomDeps(
            "Class created", simple_dep
        )
        loader = LagomLoader(container)

        loaded_class = loader.load(CustomDeps)
        assert isinstance(loaded_class, CustomDeps)
        assert loaded_class.output == "Class created"
