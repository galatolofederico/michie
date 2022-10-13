from dataclasses import dataclass

from michie.states.state import State

@dataclass
class Position(State):
    position: tuple
    heading: float = 0
