from michie.mappers.statemapper import StateMapper

class RangeAndBearingStateMapper(StateMapper):
    @classmethod
    def map(cls, state):
        return dict(
            position=state["position"],
            neighbours=state["neighbours"]
        )
    
    @classmethod
    def map(cls, mapped_state):
        range_and_bearing = []
        valid_neighbours = filter(lambda n: n["state"] != "fault", mapped_state["neighbours"]) 
        
        for neighbour in valid_neighbours:
            self_x, self_y = mapped_state["position"]["position"]
            neig_x, neig_y = neighbour["position"]["position"]
            heading = mapped_state["position"]["heading"]

            target_x, target_y = (neig_x-self_x), (neig_y-self_y)
            rotated_target_x = target_x*np.cos(-heading) - target_y*np.sin(-heading)
            rotated_target_y = target_x*np.sin(-heading) + target_y*np.cos(-heading)
            
            distance = math.sqrt(target_x**2 + target_y**2)
            rotated_heading = np.arctan2(rotated_target_y, rotated_target_x)

            range_and_bearing.append(dict(
                distance=distance,
                angle=rotated_heading,
                point=(rotated_target_x, rotated_target_y),
                beacon=dict(
                    type=neighbour["type"],
                    state=neighbour["state"],
                    level=neighbour["level"],
                    perceive_radius=neighbour["perceive_radius"]
                )
            ))
        
        return dict(
            range_and_bearing=range_and_bearing
        )