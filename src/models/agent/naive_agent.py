import numpy as np


class NaiveAgent:
    choices = []

    def __init__(self, choices):
        self.choices = choices

    def next_step(self):
        return np.random.choice(self.choices, 1)
