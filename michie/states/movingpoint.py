from michie.states.state import State
from michie.states.position import Position
from michie.states.speed import Speed

class MovingPoint(State):
    @staticmethod
    def schema():
        schema = State.schema()
        schema.update(Position.schema())
        schema.update(Speed.schema())
        return schema