from dataclasses import dataclass

from michie.states.state import State
from michie.states.position import Position
from michie.states.speed import Speed

@dataclass
class MovingPoint(State):
    position: Position
    speed: Speed