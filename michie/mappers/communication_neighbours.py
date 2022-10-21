import numpy as np
import scipy.spatial.distance
import copy

from michie.mappers.globalmapper import GlobalMapper

class CommunicationNeighboursGlobalMapper(GlobalMapper):
    def __init__(self, *, communication_key, beacon=None):
        self.communication_key = communication_key
        self.beacon = type(self).beacon if beacon is None else beacon
    
    @staticmethod
    def beacon(state):
        beacon = state.copy()
        if "neighbours" in beacon: del beacon["neighbours"]
        return beacon

    def map(self, states, global_state):
        for id, state in enumerate(states):
            dists = state["distances"]
            other_dists = np.concatenate((dists[:id], dists[id+1:]))
            other_states = states[:id] + states[id+1:]

            state["neighbours"] = []
            for nid, other_state in enumerate(other_states):
                if dists[nid] < min(states[id][self.communication_key], states[nid][self.communication_key]):
                    beacon = self.beacon(other_state)
                    assert "neighbours" not in beacon, "The neighbour beacon must not have the neighbours field"
                    state["neighbours"].append(beacon)

        return states
