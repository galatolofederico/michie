import numpy as np
import scipy.spatial.distance

from michie.mappers.globalmapper import GlobalMapper

class NeighboursGlobalMapper(GlobalMapper):
    def __init__(self, radius):
        self.radius = radius
    
    def map(self, states, global_state):
        for id, (state, dists) in enumerate(zip(states, global_state["distances"])):
            other_dists = np.concatenate((dists[:id], dists[id+1:]))
            other_states = states[:id] + states[id+1:]

            state["neighbours"] = [state for id, state in enumerate(other_states) if other_dists[id] <= self.radius]

        return states
