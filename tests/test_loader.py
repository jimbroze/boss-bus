from boss_bus.loader import ClassInstantiator


class NoDeps:
    output = "No dependencies loaded"


class TestClassInstantiator:
    def test_load_returns_instance_if_provided(self) -> None:
        loader = ClassInstantiator()
        instance = NoDeps()

        loaded_class = loader.load(instance)
        assert loaded_class.output == "No dependencies loaded"

    def test_load_instantiates_class_with_no_dependencies(self) -> None:
        loader = ClassInstantiator()

        loaded_class = loader.load(NoDeps)
        assert loaded_class.output == "No dependencies loaded"
