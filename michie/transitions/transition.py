

class Transition:
    def __init__(self, world):
        self.world = world
    
    @property
    def config(self):
        return self.world.config