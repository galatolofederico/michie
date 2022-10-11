import os
import random
from dataclasses import dataclass

import michie

class BallState(michie.State):
    position: tuple
    speed: tuple

    @classmethod
    def init(cls):
        return BallState(
            position=(
                random.randint(0, cls.config()["height"]), 
                random.randint(0, cls.config()["height"])
            ),
            speed=(
                random.randint(-5, 5),
                random.randint(-5, 5)
            )
        )

class BallMoveTransaction(michie.Transaction):
    @classmethod
    def map(cls, state):
        return dict(
            position=state.position,
            speed=state.speed
        )
    
    @classmethod
    def transact(cls, mapped_state):
        return dict(
            position=(
                mapped_state["position"][0] + mapped_state["speed"][0],
                mapped_state["position"][1] + mapped_state["speed"][1]
            )
        )


Ball = michie.Object(
    state=BallState,
    transactions=[BallMoveTransaction],
)

world = michie.World(
    config=dict(
        height=800,
        width=600
    )
)

world.add_objects(object=Ball, number=1)

world.run(
    max_ticks=10,
    workers=os.cpu_count(),
    render=True
)