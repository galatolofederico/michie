

def worker(args):
    state, transitions = args
    partial_updates = []

    for transition in transitions:
        mapped_state = transition.map(state)
        partial_update = transition.transact(mapped_state)
        state.update(partial_update)

    return state