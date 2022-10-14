from michie.mappers.statemapper import StateMapper


def NeighboursStateMapperFactory(radius):
    class NeighboursStateMapper(StateMapper):
        @classmethod
        def map(self, state, global_state):
            return state
    
    NeighboursStateMapper.__name__ = f"NeighboursStateMapper_{radius}"

    return NeighboursStateMapper