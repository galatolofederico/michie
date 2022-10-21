import numpy as np
import scipy.spatial.distance
import copy

from michie.mappers.globalmapper import GlobalMapper

class ConditionNeighboursGlobalMapper(GlobalMapper):
    def __init__(self, *, condition, beacon=None):
        self.condition = condition
        self.beacon = type(self).beacon if beacon is None else beacon
    
    @staticmethod
    def beacon(state):
        beacon = state.copy()
        if "neighbours" in beacon: del beacon["neighbours"]
        return beacon

    def map(self, states, global_state):
        for id, state in enumerate(states):
            state["neighbours"] = []
            for nid, other_state in enumerate(states):
                if self.condition(states, global_state, id, nid):
                    beacon = self.beacon(other_state)
                    assert "neighbours" not in beacon, "The neighbour beacon must not have the neighbours field"
                    state["neighbours"].append(beacon)

        return states
