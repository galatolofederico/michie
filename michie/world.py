import multiprocessing

from michie.object import Object
from michie.worker import worker

class World:
    def __init__(self, *, config=None):
        self.config = config
        self.objects = []
        self.states = None
    
    def add_object(self, object):
        assert isinstance(object, Object), "You can only add michie.Object instances"
        object.state.set_world(self)
        [transaction.set_world(self) for transaction in object.transactions]

        self.objects.append(object)
    
    def add_objects(self, *, object, number):
        for i in range(0, number):
            self.add_object(object)
    
    def run(
            self,
            *,
            workers,
            max_ticks=100,
            render=False,
        ):
        
        initial_states = [object.state.init() for object in self.objects]
        self.states = multiprocessing.Manager().list(initial_states)
        
        for i in range(0, max_ticks):
            pool = multiprocessing.Pool(processes=workers)
            results = pool.map_async(worker, zip(self.objects, self.states))
            results.wait()