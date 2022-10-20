import numpy as np
import math
from michie.mappers.statemapper import StateMapper

class RangeAndBearingStateMapper(StateMapper):
    @classmethod
    def requirements(cls, state):
        return "neighbours" in state and "position" in state
    
    @classmethod
    def global_state_map(cls, global_state):
        return dict()

    @classmethod
    def state_map(cls, state):
        return dict(
            position=state["position"],
            neighbours=state["neighbours"]
        )
    
    @classmethod
    def beacon(cls, neighbour):
        raise NotImplementedError()

    @classmethod
    def map(cls, id, mapped_state, mapped_global_state):
        range_and_bearing = []
        
        for neighbour in mapped_state["neighbours"]:
            self_x, self_y = mapped_state["position"]["position"]
            self_heading = mapped_state["position"]["heading"]
            neig_x, neig_y = neighbour["position"]["position"]
                        
            point = (neig_x - self_x, neig_y - self_y)
            
            angle = np.arctan2(point[1], point[0])%(2*math.pi) - self_heading
            distance = math.sqrt(point[0]**2 + point[1]**2)
            virtual_point = (distance*np.cos(angle), distance*np.sin(angle))

            range_and_bearing.append(dict(
                distance=float(distance),
                angle=float(angle),
                point=[float(virtual_point[0]), float(virtual_point[1])],
                beacon=cls.beacon(neighbour)
            ))
        
        return dict(
            range_and_bearing=range_and_bearing
        )