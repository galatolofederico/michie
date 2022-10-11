import multiprocessing

from michie.object import Object

class World:
    def __init__(self):
        self.objects = []
        self.states = None
    
    def add_object(self, object):
        assert isinstance(object, Object), "You can only add michie.Object instances"
        self.objects.append(object)
    
    def run(
            self,
            *,
            workers,
            max_ticks=-1,
            render=False,
        ):
        
        initial_states = [object.state.init() for object in self.objects]
        self.states = multiprocessing.Manager.list(initial_states)
