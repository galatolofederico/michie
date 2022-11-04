from enum import Enum

from michie.serialize import serialize as do_serialize
from michie.serialize import deserialize as do_deserialize


class Commands(Enum):
    ADD_OBJECT = 0
    DO_TICK = 1
    TICK_DONE = 2
    RETRIEVE_STATE = 3
    STATE = 4
    SET_STATE = 5
    EXIT = 6

def send_msg(*, to, serialize, msg):
    if serialize: msg = do_serialize(msg)
    if type(to) is dict: to = to["submit_queue"]
    to.put((serialize, msg))

def recv_msg(fr):
    if type(fr) is dict: fr = fr["results_queue"]
    deserialize, msg = fr.get()
    if deserialize: msg = do_deserialize(msg)
    return msg