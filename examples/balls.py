import os
import random
from dataclasses import dataclass

import michie
from michie.utils.init import random_point, random_speed

@dataclass
class BallState(michie.states.MovingPoint):
    color: str

Ball = michie.Object(
    state=BallState,
    transitions=[michie.transitions.MoveTransition],
)

def add_ball(world, color):
    state = random_point(bounds=dict(x=[0, 800], y=[0, 600]))
    state.update(random_speed(bounds=dict(linear_speed=[0, 5], angular_speed=[0, 0.2])))
    state.update(dict(color=color))

    world.add_object(
        object=Ball,
        init=state
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
    max_ticks=10,
    workers=os.cpu_count(),
    render=False,
    render_surface=(800, 600)
)