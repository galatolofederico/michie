from enum import Enum

from michie.serialize import serialize as do_serialize
from michie.serialize import deserialize as do_deserialize


class Commands(Enum):
    DO_TICK = 0
    TICK_DONE = 1
    RETRIEVE_STATE = 2
    STATE = 3
    SET_STATE = 4
    STATE_SET = 5
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