from src.actions import Action
from pyboy import PyBoy

class PyBoyAdapter:
    def __init__(self, pyboy: PyBoy):
        self.pyboy = pyboy

    def step(self, action: Action):
        button = None
        if action == Action.UP:
            button = "up"
        elif action == Action.DOWN:
            button = "down"
        elif action == Action.LEFT:
            button = "left"
        elif action == Action.RIGHT:
            button = "right"
        elif action == Action.A:
            button = "a"
        elif action == Action.B:
            button = "b"
        elif action == Action.START:
            button = "start"

        if button:
            self.pyboy.button_press(button)
            self.pyboy.tick()
            self.pyboy.button_release(button)

        for _ in range(23):
            self.pyboy.tick()
