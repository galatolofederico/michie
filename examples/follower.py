import michie

#https://docs.python.org/3/library/dataclasses.html

class RunnerState(michie.State):
    position: tuple
    speed: tuple

    @classmethod
    def init(cls):
        return RunnerState(
            position=random_from(cls.config["init"],.....)
            ......
        )

class RunnerMoveTransaction(michie.Transaction):
    @classmethod
    def map(cls, state):
        return dict(
            position=position,
            speed=speed
        )
    
    @classmethod
    def transact(cls, mapped_state):
        return dict(
            position=michie.utils.move_2d(
                mapped_state["position"],
                mapped_state["speed"],
                wrap_x=(0, cls.config["world_width"]),
                wrap_y=(0, cls.config["world_height"]),
            )
        )
    
class RunnerSprite(michie.Sprite):
    ....


Runner = michie.Object(
    state=RunnerState,
    transactions=[RunnerMoveTransaction],
    sprite=RunnerSprite,
)


world = michie.World()

world.add_object(Runner)
world.add_object(Runner)
world.add_object(Runner)

world.run(
    max_ticks=300,
    workers=os.cpu_count(),
    render=True
)