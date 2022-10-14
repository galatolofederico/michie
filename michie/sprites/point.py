import pygame

class PointSprite:
    def __init__(self, radius=None, color=None):
        self.radius = radius
        self.color = color
    
    def draw(self, *, window, state):
        color = "white"
        if "color" in state: color = state["color"]
        elif self.color is not None: color = self.color

        radius = 5
        if "radius" in state: radius = state["radius"]
        elif self.radius is not None: radius = self.radius

        pygame.draw.circle(window, color, state["position"]["position"], radius)