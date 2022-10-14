import json

def factory(cls):
    def decorated(**actual_args):
        setattr(cls, "args", actual_args)
        new_class_name = cls.__name__+json.dumps(actual_args)
        return type(new_class_name, cls.__bases__, dict(cls.__dict__))
    return decorated