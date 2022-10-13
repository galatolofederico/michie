import multiprocessing
import dataclasses

class Object:
    def __init__(self, *, state, transitions=[], sprites=[]):
        self.state = state
        self.transitions = transitions
        self.sprites = sprites
        self.config = None
    
    def set_config(self, config):
        self.config = config