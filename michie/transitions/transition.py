

class Transition:
    @classmethod
    def map(cls, state):
        raise NotImplementedError
    
    @classmethod
    def transact(cls, mapped_state):
        raise NotImplementedError