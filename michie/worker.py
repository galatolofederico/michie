

def worker(args):
    object, state = args
    print(state)
    partial_updates = []
    for transaction in object.transactions:
        mapped_state = transaction.map(state)
        partial_updates.append(transaction.transact(mapped_state)) 
    
    for partial_update in partial_updates:
        for key, value in partial_update.items():
            setattr(state, key, value)