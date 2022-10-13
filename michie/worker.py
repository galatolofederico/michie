import multiprocessing

class Worker(multiprocessing.Process):
    def __init__(self, *, submit_queue, results_queue, transitions):
        super(Worker, self).__init__()
        self.submit_queue = submit_queue
        self.results_queue = results_queue
        self.transitions = transitions
    
    def run(self):
        while True:
            msg, id, (state, transitions_ids) = self.submit_queue.get()
            if msg == "exit": return
            transitions = map(lambda t: self.transitions[t], transitions_ids)
            partial_updates = []

            for transition in transitions:
                mapped_state = transition.map(state)
                partial_update = transition.transact(mapped_state)
                state.update(partial_update)

            self.results_queue.put([id, state])