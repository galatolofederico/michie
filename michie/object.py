import multiprocessing
import dataclasses

class Object:
    def __init__(self, *, state, transactions):
        self.state = dataclasses.dataclass(state)
        self.transactions = transactions
        self.config = None
    
    def set_config(self, config):
        self.config = config