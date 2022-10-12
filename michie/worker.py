

def worker(args):
    state, transactions = args
    partial_updates = []
    
    for transaction in transactions:
        mapped_state = transaction.map(state)
        partial_update = transaction.transact(mapped_state)
        state.update(partial_update)
    
    return state