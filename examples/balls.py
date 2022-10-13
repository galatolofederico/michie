import os
import random
from dataclasses import dataclass

import michie
from michie.utils.init import random_position, random_speed

@dataclass
class BallState(michie.states.MovingPoint):
    color: str

Ball = michie.Object(
    state=BallState,
    transitions=[michie.transitions.MoveTransition],
    sprites=[michie.sprites.PointSprite(radius=10)]
)

def add_ball(world, color):
    state = dict(
        position=random_position(bounds=dict(x=[0, 800], y=[0, 600])),
        speed=random_speed(bounds=dict(linear_speed=[0, 5], angular_speed=[0, 0.2])),
        color=color
    )

    world.add_object(
        object=Ball,
        init=state,
    )

world = michie.World(
    config=dict(
        height=800,
        width=600
    )
)

add_ball(world, "red")
add_ball(world, "blue")
add_ball(world, "green")

world.run(
    max_ticks=1000,
    workers=os.cpu_count(),
    render=True,
    render_surface=(800, 600)
)