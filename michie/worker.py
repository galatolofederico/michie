import multiprocessing
from enum import Enum

class Works(Enum):
    EXIT = 0
    STATE_TRANSITION = 1


class Worker(multiprocessing.Process):
    def __init__(self, *, submit_queue, results_queue, transitions):
        super(Worker, self).__init__()
        self.submit_queue = submit_queue
        self.results_queue = results_queue
        self.transitions = transitions
    
    def state_transition(self, *, state, transitions_ids):
        transitions = map(lambda t: self.transitions[t], transitions_ids)
        partial_updates = []

        for transition in transitions:
            mapped_state = transition.map(state)
            partial_update = transition.transact(mapped_state)
            state.update(partial_update)
        
        return state

    def run(self):
        while True:
            work = self.submit_queue.get()
            result = None
            if work["type"] == Works.EXIT:
                return
            if work["type"] == Works.STATE_TRANSITION:
                result = self.state_transition(
                    state = work["args"]["state"],
                    transitions_ids = work["args"]["transitions_ids"]
                )
        
            self.results_queue.put(dict(
                id=work["args"]["id"],
                result=result
            ))