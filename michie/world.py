from tqdm import trange
import multiprocessing

from michie.object import Object
from michie.worker import worker

class World:
    def __init__(self, *, config=None):
        self.config = config
        self.states = []
        self.transitions = []
    
    def add_object(self, object, init):
        assert isinstance(object, Object), "You can only add michie.Object instances"
        state = object.state(**init)
        transitions = [transition(world=self) for transition in object.transitions]

        self.states.append(state)
        self.transitions.append(transitions)

    def run(
            self,
            *,
            workers,
            max_ticks=100,
            render=False,
        ):   
        pool = multiprocessing.Pool(processes=workers)
        print(self.transitions)
        for i in trange(0, max_ticks):   
            states = pool.map(worker, zip(self.states, self.transitions))
            print(states)
            exit()