import numpy as np
import scipy.spatial.distance
import copy

from michie.mappers.globalmapper import GlobalMapper

class CommunicationNeighboursGlobalMapper(GlobalMapper):
    def __init__(self, communication_key):
        self.communication_key = communication_key
    
    def map(self, states, global_state):
        for id, state in enumerate(states):
            dists = state["distances"]
            other_dists = np.concatenate((dists[:id], dists[id+1:]))
            other_states = states[:id] + states[id+1:]

            state["neighbours"] = []
            for nid, other_state in enumerate(other_states):
                if dists[nid] < min(states[id][self.communication_key], states[nid][self.communication_key]):
                    nstate = other_state.copy()
                    nstate["neighbours"] = None
                    state["neighbours"].append(nstate)

        return states
