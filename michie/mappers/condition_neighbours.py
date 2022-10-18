import numpy as np
import scipy.spatial.distance
import copy

from michie.mappers.globalmapper import GlobalMapper

class ConditionNeighboursGlobalMapper(GlobalMapper):
    def __init__(self, condition):
        self.condition = condition
    
    def map(self, states, global_state):
        for id, state in enumerate(states):
            state["neighbours"] = []
            for nid, nstate in enumerate(states):
                if self.condition(states, global_state, id, nid):
                    nstate = nstate.copy()
                    nstate["neighbours"] = None
                    state["neighbours"].append(nstate)

        return states
