import numpy as np
import scipy.spatial.distance

from michie.mappers.globalmapper import GlobalMapper

class DistancesGlobalMapper(GlobalMapper):
    def map(self, states, global_state):
        positions = np.array([state["position"]["position"] for state in states])
        
        dists = scipy.spatial.distance.pdist(positions, "euclidean")
        dists = scipy.spatial.distance.squareform(dists)
        
        global_state["distances"] = dists.tolist()

        return states