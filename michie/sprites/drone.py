import numpy as np
import math
import pygame

class DroneSprite:
    def __init__(self, color=None, height=10, width=15):
        self.color = color
        self.height = height
        self.width = width
    
    def draw(self, *, window, state):
        color = "white"
        if "color" in state: color = state["color"]
        elif self.color is not None: color = self.color

        x, y = state["position"]["position"]
        angle = state["position"]["heading"]

        points = [
            (x, y - (self.height / 2)),
            (x - (self.width / 2), y + (self.height /2)),
            (x, y + (self.height / 4)),
            (x + (self.width / 2), y + (self.height / 2)),
            (x, y - (self.height / 2)),
            (x, y + (self.height / 4)),
        ]

        position = pygame.math.Vector2((x, y))
        rotated_points = [
            (pygame.math.Vector2(p) - position) \
            .rotate_rad(angle + math.pi/2) \
            for p in points
        ]

        translated_points = [(position + p) for p in rotated_points]

        pygame.draw.polygon(
            window,
            color,
            translated_points
        )
