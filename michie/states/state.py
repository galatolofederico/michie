from dataclasses import dataclass

@dataclass
class State:
    @classmethod
    def set_world(cls, world):
        if not hasattr(cls, "world"):
            cls.world = world
        else:
            assert cls.world == world, "Can only exist one michie world"

    @classmethod
    def config(cls):
        return cls.world.config