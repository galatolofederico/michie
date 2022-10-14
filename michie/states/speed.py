from michie.states.state import State

class Speed(State):
    @staticmethod
    def schema():
        schema = State.schema()
        schema.update(dict(
            speed = dict(
                linear = float,
                angular = float
            )
        ))
        return schema
