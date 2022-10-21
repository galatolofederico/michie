import os
import random
import numpy as np
from dataclasses import dataclass

import michie
from michie.utils.init import random_position, random_speed

class RandomSpeedChange(michie.Transition):
    @classmethod
    def state_map(cls, state):
        return dict(
            speed=state["speed"]
        )

    @classmethod
    def transition(cls, state):
        new_linear_speed = state["speed"]["linear"] + random.uniform(-0.1, 0.1)
        new_linear_speed = np.clip(new_linear_speed, 0, 5)
        
        new_angular_speed = state["speed"]["angular"] + random.uniform(-0.01, 0.01)
        new_angular_speed = np.clip(new_angular_speed, -0.2, 0.2)

        return dict(
            speed=dict(
                linear=float(new_linear_speed),
                angular=float(new_angular_speed)
            )
        )

def add_drone(world, color):
    init = dict(
        **random_position(bounds=dict(x=[0, 800], y=[0, 600])),
        **random_speed(bounds=dict(linear_speed=[0, 5], angular_speed=[-0.2, 0.2])),
        color=color
    )

    Drone = michie.Object(
        name="Drone",
        init=init,
        transitions=[
            michie.transitions.MoveTransition,
            RandomSpeedChange
        ],
        sprites=[
            michie.sprites.DroneSprite(width=20, height=30)
        ]
    )

    world.add_object(Drone)

world = michie.World()

for _ in range(0, 30): add_drone(world, "red")
for _ in range(0, 30): add_drone(world, "green")
for _ in range(0, 30): add_drone(world, "blue")

world.run(
    max_ticks=1000,
    workers=os.cpu_count(),
    render=True,
    render_fps=30,
    render_surface=(800, 600)
)