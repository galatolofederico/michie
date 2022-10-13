from dataclasses import dataclass

from michie.states.state import State

class Position(State):
    @staticmethod
    def schema():
        return dict(
            position = dict(
                position = tuple,
                heading = float
            )
        )
