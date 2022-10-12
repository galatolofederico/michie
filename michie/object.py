import multiprocessing
import dataclasses

class StatefulObject:
    def __init__(self, *, state, transactions, world, config=None):
        self.state = state(world=world, id=len(world.objects))
        self.transactions = [transaction(world=world) for transaction in transactions]
        self.config = config
        self.world = world

class Object:
    def __init__(self, *, state, transactions):
        self.state = state
        self.transactions = transactions
        self.config = None
    
    def set_config(self, config):
        self.config = config
    
    def factory(self, world):        
        return StatefulObject(
            state=self.state,
            transactions=self.transactions,
            config=self.config,
            world=world
        )