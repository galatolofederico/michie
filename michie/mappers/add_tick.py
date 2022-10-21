from michie.mappers.globalmapper import GlobalMapper

class AddTickGlobalMapper(GlobalMapper):
    def map(self, states, global_state):
        for state in states:
            state["tick"] = global_state["tick"]

        return states
