import multiprocessing

from michie.object import Object
from michie.worker import worker

class World:
    def __init__(self, *, config=None):
        self.config = config
        self.objects = []
    
    def add_object(self, object):
        assert isinstance(object, Object), "You can only add michie.Object instances"
        self.objects.append(object.factory(self))
    
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

        states = [object.state.get() for object in self.objects]
        transactions = [object.transactions for object in self.objects]        
        pool = multiprocessing.Pool(processes=workers)

        for i in range(0, max_ticks):   
            states = pool.map(worker, zip(states, transactions))
            print(states)