from dataclasses import dataclass

from michie.states.point import Point

@dataclass
class Speed:
    linear: float
    angular: float

@dataclass
class MovingPoint(Point):
    speed: Speed