

class StateMapper:
    @classmethod
    def sync(cls):
        return False
    
    @classmethod
    def requirements(cls, state):
        return True

    @classmethod
    def state_map(cls, state):
        raise NotImplementedError()
    
    @classmethod
    def global_state_map(cls, state):
        raise NotImplementedError()
    
    @classmethod
    def map(cls, id, mapped_state, mapped_global_state):
        raise NotImplementedError()