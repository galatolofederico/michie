import pygame

class PointSprite:
    def __init__(self, radius, color=None):
        self.radius = radius
        self.color = color
    
    def draw(self, *, window, state):
        color = "white"
        if "color" in state: color = state["color"]
        elif self.color is not None: color = self.color
        print(state)
        pygame.draw.circle(window, color, state["position"]["position"], self.radius)