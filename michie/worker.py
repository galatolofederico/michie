import multiprocessing
from enum import Enum

from michie.messages import send_msg, recv_msg
from michie.messages import Commands

class Worker(multiprocessing.Process):
    def __init__(self, *, id, submit_queue, results_queue, retrieve_map_state):
        super(Worker, self).__init__()
        self.id = id
        self.submit_queue = submit_queue
        self.results_queue = results_queue
        self.retrieve_map_state = retrieve_map_state
        self.objects = []
        self.dict_states = []

    def tick(self, global_state):
        for object, state in zip(self.objects, self.dict_states):
            for state_mapper in object.state_mappers:
                mapped_global_state = state_mapper.mapped_global_state(global_state)
                mapped_state = state_mapper.state_map(state)
                state.update(state_mapper.map(
                    object.id,
                    mapped_state,
                    mapped_global_state
                ))
            
            for transition in object.transitions:
                mapped_state = transition.state_map(state)
                state.update(transition.transition(mapped_state))
        
        send_msg(
            to=self.results_queue,
            serialize=False,
            msg=dict(
                cmd=Commands.TICK_DONE.value,
            )
        )

    def retrieve_state(self):
        states = []
        for object, state in zip(self.objects, self.dict_states):
            states.append(dict(
                worker_id=self.id,
                object_id=object.id,
                state=self.retrieve_map_state(state)
            ))
        
        send_msg(
            to=self.results_queue,
            serialize=True,
            msg=dict(
                cmd=Commands.STATE.value,
                args=dict(
                    states=states
                )
            )
        )

    def run(self):
        while True:
            cmd = recv_msg(self.submit_queue) 
            args = cmd["args"]
            cmd = cmd["cmd"]
            if cmd == Commands.ADD_OBJECT.value:
                self.objects.append(args["object"])
                self.dict_states.append(args["object"].init)
            elif cmd == Commands.DO_TICK.value:
                self.tick(global_state=args["global_state"])
            elif cmd == Commands.RETRIEVE_STATE.value:
                self.retrieve_state()
            elif cmd == Commands.EXIT.value:
                exit()
            else:
                raise Exception(f"Unknown command {cmd}")