

class Transaction:
    @classmethod
    def set_world(cls, world):
        if not hasattr(cls, "world"):
            cls.world = world
        else:
            assert cls.world == world, "Can only exist one michie world"