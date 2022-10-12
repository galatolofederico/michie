from dataclasses import dataclass

from michie.states.state import State

@dataclass
class Point(State):
    position: tuple
