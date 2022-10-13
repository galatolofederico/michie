import numpy as np
import pygame

class HeadingSprite:
    def __init__(self, color=None, length=30, width=3):
        self.color = color
        self.length = length
        self.width = width
    
    def draw(self, *, window, state):
        color = "white"
        if "color" in state: color = state["color"]
        elif self.color is not None: color = self.color

        start = state["position"]["position"]
        end = (
            state["position"]["position"][0] + self.length*np.cos(state["position"]["heading"]),
            state["position"]["position"][1] + self.length*np.sin(state["position"]["heading"])
        )

        pygame.draw.line(window, color, start, end, self.width)