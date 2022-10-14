import numpy as np

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
        x_k, y_k = mapped_state["position"]["position"]
        theta_k = mapped_state["position"]["heading"]
        v_k = mapped_state["speed"]["linear"]
        w_k = mapped_state["speed"]["angular"]

        if abs(w_k) <= 0.0175:
            theta_k1 = theta_k
            x_k1 = x_k + v_k*np.cos(theta_k)
            y_k1 = y_k + v_k*np.sin(theta_k)
        else:
            theta_k1 = theta_k + w_k
            x_k1 = x_k + (v_k/w_k)*(np.sin(theta_k1) - np.sin(theta_k))
            y_k1 = y_k - (v_k/w_k)*(np.cos(theta_k1) - np.cos(theta_k)) 

        mapped_state["position"]["position"] = (x_k1, y_k1)
        mapped_state["position"]["heading"] = theta_k1
        
        return mapped_state