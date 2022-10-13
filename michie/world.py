import dataclasses
from tqdm import trange
import multiprocessing

from michie.object import Object
from michie.worker import worker

class World:
    def __init__(self, *, config=None):
        self.config = config
        self.objects = []
        self.states = []
        self.transitions = []
    
    def add_object(self, object, init):
        assert isinstance(object, Object), "You can only add michie.Object instances"
        state = object.state(**init)
        transitions = [transition(world=self) for transition in object.transitions]

        self.objects.append(object)
        self.states.append(state)
        self.transitions.append(transitions)

    def transitions_tick(self, pool):
        #TODO: opt-in per dataclass=>dict=>dataclass
        #      di default fare dataclass=>dict all'inizio e poi usare solo i dict
        dict_states = [dataclasses.asdict(state) for state in self.states]
        updated_states = pool.map(worker, zip(dict_states, self.transitions))
        self.states = [object.state(**state) for object, state in zip(self.objects, updated_states)]

    def run(
            self,
            *,
            workers,
            max_ticks=100,
            render=False,
        ):   
        pool = multiprocessing.Pool(processes=workers)
        for i in trange(0, max_ticks):
            self.transitions_tick(pool)