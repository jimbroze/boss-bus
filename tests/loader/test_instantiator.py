from boss_bus.loader.instantiator import ClassInstantiator
from boss_bus.message_bus import MessageBus
from tests.loader.examples import BusDeps, LayeredDeps, NoDeps, SimpleDeps


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

    def test_load_returns_message_bus_if_provided(
        self,
    ) -> None:
        bus = MessageBus()
        loader = ClassInstantiator([bus])

        loaded_class = loader.load(BusDeps)
        assert isinstance(loaded_class, BusDeps)
        assert loaded_class.bus == bus

    def test_message_bus_instance_can_be_added_to_instantiator(
        self,
    ) -> None:
        loader = ClassInstantiator()
        bus = MessageBus()
        loader.add_dependency(bus)

        loaded_class = loader.load(BusDeps)
        assert isinstance(loaded_class, BusDeps)
        assert loaded_class.bus == bus
