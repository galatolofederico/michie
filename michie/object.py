import dataclasses

#TODO: se rimane cosi questa è una dataclass
class Object:
    def __init__(self, *, state, transactions):
        assert dataclasses.is_dataclass(state), "Michie States must be dataclasses, use @dataclass decorator"
        self.state = state
        self.transactions = transactions
    