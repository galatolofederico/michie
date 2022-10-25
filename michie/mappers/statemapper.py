

class StateMapper:
    @classmethod
    def sync(cls):
        return False
    
    @classmethod
    def requirements(cls, state):
        return True

    @classmethod
    def map_state(cls, state):
        raise NotImplementedError()
    
    @classmethod
    def map_global_state(cls, state):
        raise NotImplementedError()
    
    @classmethod
    def map(cls, id, mapped_state, mapped_global_state):
        raise NotImplementedError()