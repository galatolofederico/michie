import numpy as np
import scipy.spatial.distance
import copy

from michie.mappers.globalmapper import GlobalMapper

class NeighboursGlobalMapper(GlobalMapper):
    def __init__(self, radius):
        self.radius = radius
    
    def map(self, states, global_state):
        for id, state in enumerate(states):
            dists = state["distances"]
            other_dists = np.concatenate((dists[:id], dists[id+1:]))
            other_states = states[:id] + states[id+1:]

            state["neighbours"] = []
            for id, other_state in enumerate(other_states):
                if other_dists[id] <= self.radius:
                    nstate = other_state.copy()
                    nstate["neighbours"] = None
                    state["neighbours"].append(nstate)

        return states
