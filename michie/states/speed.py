from dataclasses import dataclass

from michie.states.state import State

@dataclass
class Speed(State):
    linear: float
    angular: float