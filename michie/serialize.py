import orjson

def serialize(obj):
    return orjson.dumps(obj)

def deserialize(bytes):
    return orjson.loads(bytes)