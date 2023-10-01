import os

from .environment import Environment
from .agent import Agent


orientations = ['right', 'down', 'left', 'up']


class Episode:
    def __init__(self):
        self.environment = Environment(4, 4)
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
        while not self.agent.is_dead() or not self.agent.exited():
            self.environment.print_grid()
            percepts = self.environment.get_percepts(action)
            print(f"Current loc: {self.agent.location}")
            print(f"facing: {self.agent.orientations[self.agent.orientation]}")
            # print(f"Points: {self.points}")
            print(f"Observed: {percepts}")
            action = input("Enter your action: ")

            # grabbed_gold = percepts["grabbed_gold"]
            # if grabbed_gold:
            #     self.agent.grab_gold()

            # # os.system('clear')
            # self.environment.print_grid()

            # self.points += percepts["points"]
            # if percepts["agent_dead"]:
            #     print(f"Agent is dead. Total Points: {self.points} {percepts}")
            #     return

            # if percepts["bump"]:
            #     self.loc = tuple(list(self.oldloc))

            # orientation = orientations[self.orientation_idx]

            # print(f"Current loc: {self.loc}")
            # print(f"facing: {orientation}")
            # print(f"Points: {self.points}")
            # print(f"Observed: {percepts}")
            # action = input("Enter your action: ")

            # if action == 'f':
            #     self.oldloc = tuple(list(self.loc))

            #     if (orientation == 'right'):
            #         self.loc = (self.loc[0], self.loc[1]+1)
            #     elif (orientation == 'left'):
            #         self.loc = (self.loc[0], self.loc[1]-1)
            #     elif (orientation == 'up'):
            #         self.loc = (self.loc[0]+1, self.loc[1])
            #     elif (orientation == 'down'):
            #         self.loc = (self.loc[0]-1, self.loc[1])
            # elif action == 'l':
            #     self.orientation_idx = (
            #         self.orientation_idx-1) % len(orientations)
            # elif action == 'r':
            #     self.orientation_idx = (
            #         self.orientation_idx+1) % len(orientations)
            # elif action == 'g':
            #     pass
            # elif action == 's':
            #     pass
            # else:
            #     print("Unrecognized action")
