import multiprocessing
import orjson
from enum import Enum

class Works(Enum):
    EXIT = 0
    STATE_MAP = 1
    STATE_TRANSITION = 2


class Worker(multiprocessing.Process):
    def __init__(self, *, submit_queue, results_queue, state_mappers, transitions):
        super(Worker, self).__init__()
        self.submit_queue = submit_queue
        self.results_queue = results_queue
        self.state_mappers = state_mappers
        self.transitions = transitions
    
    def state_transition(self, *, state, transitions_ids):
        transitions = map(lambda t: self.transitions[t], transitions_ids)
        partial_updates = []

        for transition in transitions:
            mapped_state = transition.map(state)
            partial_update = transition.transact(mapped_state)
            state.update(partial_update)
        
        return state

    def state_map(self, *, id, state, global_state, state_mappers_ids):
        state_mappers = map(lambda t: self.state_mappers[t], state_mappers_ids)
        partial_updates = []

        for state_mapper in state_mappers:
            mapped_state = state_mapper.map(id, state, global_state)
            state.update(mapped_state)
        
        return state

    def run(self):
        while True:
            work = self.submit_queue.get()
            #work = orjson.loads(work)
            #print(work)
            result = None
            if work["type"] == Works.EXIT.value:
                return
            if work["type"] == Works.STATE_MAP.value:
                result = self.state_map(
                    id = work["args"]["id"],
                    state = work["args"]["state"],
                    #global_state = orjson.loads(work["args"]["global_state"]),
                    global_state = work["args"]["global_state"],
                    state_mappers_ids = work["args"]["state_mappers_ids"]
                )
            if work["type"] == Works.STATE_TRANSITION.value:
                result = self.state_transition(
                    state = work["args"]["state"],
                    transitions_ids = work["args"]["transitions_ids"]
                )
            
            self.results_queue.put(dict(
                id=work["args"]["id"],
                result=result
            ))