import pygame
import os
import random
from dataclasses import dataclass
from collections import Counter

import michie
from michie.utils.init import random_position, random_speed

class MutateTransition(michie.Transition):
    @classmethod
    def state_map(cls, state):
        return dict(
            neighbours_colors=list(map(lambda n: n["color"], state["neighbours"]))
        )
    
    @classmethod
    def transact(cls, mapped_state):
        max_count = Counter(mapped_state["neighbours_colors"]).most_common(1)
        if len(max_count) > 0:
            color = max_count[0][0]
            return dict(
                color=color
            )
        
        return dict()

class FilterNeighboursMapper(michie.StateMapper):
    @classmethod
    def global_state_map(cls, global_state):
        return dict()
    
    @classmethod
    def state_map(cls, state):
        return dict(
            neighbours=state["neighbours"]
        )
    
    @classmethod
    def map(cls, id, mapped_state, global_state):
        neighbours = list(filter(lambda n: n["type"] == "FixedBall", mapped_state["neighbours"]))
        return dict(neighbours=neighbours)

class NeighboursRadiusSprite(michie.Sprite):
    def __init__(self, radius):
        self.radius = radius
    
    def draw(self, *, window, state):
        pygame.draw.circle(window, "white", state["position"]["position"], self.radius, 1)



def add_fixed_ball(world, color):
    init = dict(
        **random_position(bounds=dict(x=[0, 800], y=[0, 600])),
        **random_speed(bounds=dict(linear_speed=[0, 5], angular_speed=[0, 0])),
        color=color
    )

    FixedBall = michie.Object(
        name="FixedBall",
        init=init,
        transitions=[
            michie.transitions.WrappedMoveTransitionFactory(bounds=[800, 600])
        ],
        sprites=[michie.sprites.PointSprite(radius=3)]
    )

    world.add_object(FixedBall)

def add_mutating_ball(world):
    init = dict(
        **random_position(bounds=dict(x=[0, 800], y=[0, 600])),
        **random_speed(bounds=dict(linear_speed=[0, 5], angular_speed=[0, 0])),
        color="white"
    )

    MutatingBall = michie.Object(
        name="MutatingBall",
        init=init,
        state_mappers=[
            FilterNeighboursMapper
        ],
        transitions=[
            michie.transitions.WrappedMoveTransitionFactory(bounds=[800, 600]),
            MutateTransition
        ],
        sprites=[
            michie.sprites.PointSprite(radius=10),
            NeighboursRadiusSprite(radius=100)
        ]
    )


    world.add_object(MutatingBall)

world = michie.World(
    global_mappers=[
        michie.mappers.DistancesGlobalMapper(),
        michie.mappers.NeighboursGlobalMapper(radius=100)
    ],
)

for _ in range(0, 10): add_mutating_ball(world)
for _ in range(0, 30): add_fixed_ball(world, "red")
for _ in range(0, 30): add_fixed_ball(world, "green")
for _ in range(0, 30): add_fixed_ball(world, "blue")

world.run(
    max_ticks=1000,
    workers=os.cpu_count(),
    #render=True,
    render_fps=30,
    render_surface=(800, 600)
)