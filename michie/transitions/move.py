import math
import numpy as np

from michie.transitions.transition import Transition
from michie.factory import factory

class MoveTransition(Transition):
    @classmethod
    def state_map(cls, state):
        return dict(
            position=state["position"],
            speed=state["speed"]
        )
    
    @classmethod
    def transition(cls, mapped_state):
        x_k, y_k = mapped_state["position"]["position"]
        theta_k = mapped_state["position"]["heading"]
        v_k = mapped_state["speed"]["linear"]
        w_k = mapped_state["speed"]["angular"]

        if abs(w_k) <= 0.0175:
            theta_k1 = theta_k
            x_k1 = x_k + v_k*np.cos(theta_k)
            y_k1 = y_k + v_k*np.sin(theta_k)
        else:
            theta_k1 = (theta_k + w_k) % (2*math.pi)
            x_k1 = x_k + (v_k/w_k)*(np.sin(theta_k1) - np.sin(theta_k))
            y_k1 = y_k - (v_k/w_k)*(np.cos(theta_k1) - np.cos(theta_k)) 

        return dict(
            position=dict(
                position=(float(x_k1), float(y_k1)),
                heading=float(theta_k1)
            )
        )


@factory
class WrappedMoveTransitionFactory(Transition):
    @classmethod
    def state_map(cls, state):
        return MoveTransition.state_map(state)
    
    @classmethod
    def transition(cls, mapped_state):
        mapped_state = MoveTransition.transition(mapped_state)
        mapped_state["position"]["position"] = (
            mapped_state["position"]["position"][0] % cls.args["bounds"][0],
            mapped_state["position"]["position"][1] % cls.args["bounds"][1],
        )
        return mapped_state


class EulerMoveTransition(Transition):
    @classmethod
    def state_map(cls, state):
        return dict(
            position=state["position"],
            speed=state["speed"]
        )
    
    @classmethod
    def transition(cls, mapped_state):
        x_k, y_k = mapped_state["position"]["position"]
        theta_k = mapped_state["position"]["heading"]
        v_k = mapped_state["speed"]["linear"]
        w_k = mapped_state["speed"]["angular"]

        x_k1 = x_k + v_k*np.cos(theta_k)
        y_k1 = y_k + v_k*np.sin(theta_k)
        theta_k1 = (theta_k + w_k)%(2*math.pi)

        return dict(
            position=dict(
                position=(float(x_k1), float(y_k1)),
                heading=float(theta_k1)
            )
        )