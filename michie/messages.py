from enum import Enum
import orjson

class Serializer(Enum):
    CPICKLE = 0
    ORJSON = 1

class Command(Enum):
    DO_TICK = 0
    TICK_DONE = 1
    RETRIEVE_STATE = 2
    STATE = 3
    SET_STATE = 4
    STATE_SET = 5
    EXIT = 6

def serialize(serializer, obj):
    if serializer == Serializer.ORJSON.value:
        return orjson.dumps(obj)
    else:
        raise Exception("Unknown serializer")

def deserialize(serializer, bytes):
    if serializer == Serializer.ORJSON.value:
        return orjson.loads(bytes)
    else:
        raise Exception("Unknown serializer")

def send_msg(*, to, serializer, msg, stats=None):
    cmd = msg["cmd"]
    serialized = serialize(serializer, msg)
    if type(to) is dict: to = to["submit_queue"]

    if stats is not None: update_stats(
        cmd = cmd,
        size = len(serialized),
        scope = "send"
    )
    to.put((serializer, serialized))

def recv_msg(fr, stats=None):
    if type(fr) is dict: fr = fr["results_queue"]
    deserializer, msg = fr.get()
    deserialized = deserialize(deserializer, msg)
    cmd = deserialized["cmd"]
    
    if stats is not None: update_stats(
        cmd = cmd,
        size = len(msg),
        scope = "receive"
    )
    return deserialized