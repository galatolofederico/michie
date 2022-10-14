from dataclasses import dataclass

from michie.states.state import State

class Position(State):
    @staticmethod
    def schema():
        schema = State.schema()
        schema.update(dict(
            position = dict(
                position = tuple,
                heading = float
            )
        ))
        return schema
