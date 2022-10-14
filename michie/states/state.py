from schema import Schema

class State:
    @staticmethod
    def schema():
        return dict(
            type = str
        )
    
    @classmethod
    def validate(cls, state):
        try:
            Schema(cls.schema()).validate(state)
        except Exception as e:
            print(f"Schema validation error:\n{e}\n\nSchema: {cls.schema()}\nState: {state}")
            exit()