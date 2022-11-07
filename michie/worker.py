import multiprocessing
from enum import Enum

from michie.messages import send_msg, recv_msg
from michie.messages import Command, Serializer

class Worker(multiprocessing.Process):
    def __init__(self, *, id, submit_queue, results_queue, retrieve_map_state):
        super(Worker, self).__init__()
        self.id = id
        self.submit_queue = submit_queue
        self.results_queue = results_queue
        self.retrieve_map_state = retrieve_map_state
        self.objects = dict()
        self.states = dict()

    def add_object(self, object):
        assert not object.id in self.objects
        self.objects[object.id] = object
        self.states[object.id] = object.init

    def tick(self, global_state):
        for object, state in zip(self.objects.values(), self.states.values()):
            for state_mapper in object.state_mappers:
                mapped_global_state = state_mapper.global_state_map(global_state)
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
            serializer=Serializer.ORJSON.value,
            msg=dict(
                cmd=Command.TICK_DONE.value,
            )
        )

    def retrieve_state(self):
        states = []
        for object, state in zip(self.objects.values(), self.states.values()):
            states.append(dict(
                worker_id=self.id,
                object_id=object.id,
                state=self.retrieve_map_state(state)
            ))
        
        send_msg(
            to=self.results_queue,
            serializer=Serializer.ORJSON.value,
            msg=dict(
                cmd=Command.STATE.value,
                args=dict(
                    states=states
                )
            )
        )

    def set_states(self, states):
        for state in states:
            self.states[state["object_id"]] = state["state"]
        
        send_msg(
            to=self.results_queue,
            serializer=Serializer.ORJSON.value,
            msg=dict(
                cmd=Command.STATE_SET.value,
                args=dict()
            )
        )

    def run(self):
        while True:
            cmd = recv_msg(self.submit_queue) 
            args = cmd["args"]
            cmd = cmd["cmd"]
            if cmd == Command.DO_TICK.value:
                self.tick(global_state=args["global_state"])
            elif cmd == Command.RETRIEVE_STATE.value:
                self.retrieve_state()
            elif cmd == Command.SET_STATE.value:
                self.set_states(states=args["states"])
            elif cmd == Command.EXIT.value:
                exit()
            else:
                raise Exception(f"Unknown command {cmd}")