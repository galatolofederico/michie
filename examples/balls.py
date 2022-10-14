import os
import random
from dataclasses import dataclass

import michie
from michie.utils.init import random_position, random_speed

@dataclass
class BallState(michie.State):
    @staticmethod
    def schema():
        schema = michie.State.schema()
        schema.update(michie.states.MovingPoint.schema())
        schema.update(dict(color=str))
        return schema

Ball = michie.Object(
    name="Ball",
    state=BallState,
    transitions=[michie.transitions.MoveTransition],
    sprites=[michie.sprites.PointSprite(radius=10), michie.sprites.HeadingSprite()]
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

for _ in range(0, 15): add_ball(world, "red")
for _ in range(0, 15): add_ball(world, "green")
for _ in range(0, 15): add_ball(world, "blue")

world.run(
    max_ticks=1000,
    workers=os.cpu_count(),
    render=True,
    render_fps=30,
    render_surface=(800, 600)
)