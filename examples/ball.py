import os
import michie

class BallState(michie.State):
    position: tuple
    speed: tuple

    @classmethod
    def init(cls):
        return BallState(
            position=(0, 0),
            speed=(1, 1)
        )

class BallMoveTransaction(michie.Transaction):
    @classmethod
    def map(cls, state):
        return dict(
            position=position,
            speed=speed
        )
    
    @classmethod
    def transact(cls, mapped_state):
        return dict(
            position=(
                mapped_state["position"][0] + mapped_state["state"][0],
                mapped_state["position"][1] + mapped_state["state"][1]
            )
        )


Ball = michie.Object(
    state=BallState,
    transactions=[BallMoveTransaction],
)

world = michie.World()

world.add_object(Ball)

world.run(
    max_ticks=300,
    workers=os.cpu_count(),
    render=True
)