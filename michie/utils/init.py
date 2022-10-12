import random

def random_point(*, bounds):
    return dict(
        position=(
            random.uniform(*bounds["x"]),
            random.uniform(*bounds["y"]),
        )
    )

def random_speed(*, bounds):
    return dict(
        speed=dict(
            linear=random.uniform(*bounds["linear_speed"]),
            angular=random.uniform(*bounds["angular_speed"])
        )
    )