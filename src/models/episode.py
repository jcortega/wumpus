import os

from .environment import Environment
from .agent import Agent


orientations = ['right', 'down', 'left', 'up']


class Episode:
    def __init__(self, debug):
        self.debug = debug
        self.environment = Environment(4, 4, debug=debug)
        self.agent = Agent()
        self.environment.set_agent(self.agent)

        self.oldloc = (0, 0)
        self.loc = (0, 0)
        self.orientation_idx = 0
        self.points = 0
        self.grabbed_gold = False

    def run(self):
        print("Running episode...")

        action = None
        while True:
            self.environment.print_grid()
            percepts = self.environment.get_percepts(action)
            if self.debug:
                print(f"Current loc: {self.agent.location}")
                print(
                    f"facing: {self.agent.orientations[self.agent.orientation]}")
                print(f"Points: {self.agent.points()}")
                print(f"Observed: {percepts}")
            if self.agent.is_dead():
                self.environment.print_grid()
                print(
                    f"Agent died leaving with {self.agent.points()} points")
                return

            if self.agent.exited():
                self.environment.print_grid()
                print(f"Agent exited with {self.agent.points()} points.")
                return True

            action = input("Enter your action: ")
