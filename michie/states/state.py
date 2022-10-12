from dataclasses import dataclass

class State:
    def __init__(self, world):
        self.state = dict()
        self.world = world

    def update(self, state):
        self.state.update(state)
    
    def get(self):
        return self.state.copy()

    @property
    def config(self):
        return self.world.config