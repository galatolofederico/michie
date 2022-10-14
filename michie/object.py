import multiprocessing
import dataclasses

class Object:
    def __init__(self, *, name, state, state_mappers=[], transitions=[], sprites=[]):
        self.name = name
        self.state = state
        self.state_mappers = state_mappers
        self.transitions = transitions
        self.sprites = sprites
        self.config = None
    
    def set_config(self, config):
        self.config = config