from copy import deepcopy

from .environment import Environment
from .agent import Agent


orientations = ['right', 'down', 'left', 'up']


class Episode:
    def __init__(self):
        self.environment = Environment(4, 4)
        self.agent = Agent()
        self.oldloc = (0, 0)
        self.loc = (0, 0)
        self.orientation_idx = 0
        self.points = 0

    def run(self):
        print("Running episode...")
        self.environment.print_grid()

        action = None
        while True:
            percepts = self.environment.get_percepts(
                self.oldloc, self.loc, action)
            self.points += percepts["points"]
            if percepts["agent_dead"]:
                print(f"Agent is dead. Total Points: {self.points}")
                return

            if percepts["bump"]:
                self.loc = deepcopy(self.oldloc)

            orientation = orientations[self.orientation_idx]

            print(f"Current loc: {self.loc}")
            print(f"facing: {orientation}")
            print(f"Points: {self.points}")
            print(f"Observed: {percepts}")
            action = input("Enter your action: ")

            if action == 'f':
                self.oldloc = tuple(list(self.loc))

                if (orientation == 'right'):
                    self.loc = (self.loc[0], self.loc[1]+1)
                elif (orientation == 'left'):
                    self.loc = (self.loc[0], self.loc[1]-1)
                elif (orientation == 'up'):
                    self.loc = (self.loc[0]+1, self.loc[1])
                elif (orientation == 'down'):
                    self.loc = (self.loc[0]-1, self.loc[1])
            elif action == 'l':
                self.orientation_idx = (
                    self.orientation_idx-1) % len(orientations)
            elif action == 'r':
                self.orientation_idx = (
                    self.orientation_idx+1) % len(orientations)
            elif action == 'g':
                pass
            elif action == 's':
                pass
            else:
                print("Unrecognized action")
