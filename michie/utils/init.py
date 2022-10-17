import random
import math

def random_position(*, bounds):
    return dict(
        position=dict(
            position=(
                random.uniform(*bounds["x"]),
                random.uniform(*bounds["y"]),
            ),
            heading=random.uniform(0, 2*math.pi)
        )
    )

def random_speed(*, bounds):
    return dict(
        speed=dict(
            linear=random.uniform(*bounds["linear_speed"]),
            angular=random.uniform(*bounds["angular_speed"])
        )
    )