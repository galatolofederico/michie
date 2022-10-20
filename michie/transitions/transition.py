

class Transition:
    @classmethod
    def requirements(cls, state):
        return True

    @classmethod
    def state_map(cls, state):
        raise NotImplementedError
    
    @classmethod
    def transition(cls, mapped_state):
        raise NotImplementedError