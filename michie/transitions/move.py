from michie.transitions.transition import Transition

class MoveTransition(Transition):
    @classmethod
    def map(cls, state):
        return dict(
            position=state["position"],
            speed=state["speed"]
        )
    
    @classmethod
    def transact(cls, mapped_state):
        return mapped_state