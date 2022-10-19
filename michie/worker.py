import multiprocessing
import orjson
from enum import Enum

class Works(Enum):
    EXIT = 0
    STATE_MAP = 1
    STATE_TRANSITION = 2


class Worker(multiprocessing.Process):
    def __init__(self, *, id, submit_queue, results_queue, state_mappers, transitions):
        super(Worker, self).__init__()
        self.id = id
        self.submit_queue = submit_queue
        self.results_queue = results_queue
        self.state_mappers = state_mappers
        self.transitions = transitions

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
            result = None
            if work["type"] == Works.EXIT.value:
                return
            if work["type"] == Works.STATE_MAP.value:
                result = self.state_mappers[
                    work["args"]["state_mapper_id"]
                ].map(work["args"]["id"], work["args"]["state"], work["args"]["global_state"])

            if work["type"] == Works.STATE_TRANSITION.value:
                result = self.transitions[
                    work["args"]["transition_id"]
                ].transact(work["args"]["state"])

            self.results_queue.put(dict(
                id=work["args"]["id"],
                result=result
            ))