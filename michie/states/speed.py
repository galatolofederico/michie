from michie.states.state import State

class Speed(State):
    @staticmethod
    def schema():
        return dict(
            speed = dict(
                linear = float,
                angular = float
            )
        )
