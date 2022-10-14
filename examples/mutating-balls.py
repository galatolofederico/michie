import os
import random
from dataclasses import dataclass
from collections import Counter

import michie
from michie.utils.init import random_position, random_speed

@dataclass
class BallState(michie.State):
    @staticmethod
    def schema():
        schema = dict()
        schema.update(michie.states.MovingPoint.schema())
        schema.update(dict(color=str))
        return schema

class MutateTransition(michie.Transition):
    @classmethod
    def map(cls, state):
        return dict(
            neighbours_colors=list(map(lambda n: n["color"], state["neighbours"]))
        )
    
    @classmethod
    def transact(cls, mapped_state):
        max_count = Counter(mapped_state["neighbours_colors"]).most_common(1)
        if len(max_count) > 0:
            mapped_state["color"] = max_count[0][0]
        return mapped_state

class FilterNeighboursMapper(michie.StateMapper):
    @classmethod
    def map(cls, id, state, global_state):
        state["neighbours"] = list(filter(lambda n: n["type"] == "FixedBall", state["neighbours"]))
        return state

FixedBall = michie.Object(
    name="FixedBall",
    state=BallState,
    transitions=[
        michie.transitions.WrappedMoveTransitionFactory([800, 600])
    ],
    sprites=[michie.sprites.PointSprite(radius=3)]
)

MutatingBall = michie.Object(
    name="MutatingBall",
    state=BallState,
    transitions=[
        michie.transitions.WrappedMoveTransitionFactory([800, 600]),
        MutateTransition
    ],
    sprites=[michie.sprites.PointSprite(radius=10)]
)

def add_fixed_ball(world, color):
    state = dict(
        position=random_position(bounds=dict(x=[0, 800], y=[0, 600])),
        speed=random_speed(bounds=dict(linear_speed=[0, 5], angular_speed=[0, 0])),
        color=color
    )

    world.add_object(
        object=FixedBall,
        init=state,
    )

def add_mutating_ball(world):
    state = dict(
        position=random_position(bounds=dict(x=[0, 800], y=[0, 600])),
        speed=random_speed(bounds=dict(linear_speed=[0, 5], angular_speed=[0, 0])),
        color="white"
    )

    world.add_object(
        object=MutatingBall,
        init=state,
    )

world = michie.World(
    global_mappers=[
        michie.mappers.DistancesGlobalMapper(),
        michie.mappers.NeighboursGlobalMapper(radius=100)
    ],
    state_mappers=[
        FilterNeighboursMapper
    ]
)

for _ in range(0, 5): add_mutating_ball(world)
for _ in range(0, 15): add_fixed_ball(world, "red")
for _ in range(0, 15): add_fixed_ball(world, "green")
for _ in range(0, 15): add_fixed_ball(world, "blue")

world.run(
    max_ticks=1000,
    workers=os.cpu_count(),
    render=True,
    render_fps=30,
    render_surface=(800, 600)
)