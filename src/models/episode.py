import time
import numpy as np

from .environment import Environment
from .agent.naive_agent import NaiveAgent
from .agent.human_agent import HumanAgent


class Episode:
    def __init__(self, debug):
        self.debug = debug
        self.environment = Environment(4, 4, False, 0.2, debug=debug)
        self.agent = self.environment.get_agent_state()

        self.oldloc = (0, 0)
        self.loc = (0, 0)
        self.orientation_idx = 0
        self.points = 0
        self.grabbed_gold = False

    def run(self, agent_type='naive'):
        print(f"Running episode with {agent_type} agent...")

        actions = {'f': 'Forward', 'l': 'TurnLeft',
                   'r': 'Turning Right', 's': 'Shooting wumpus', 'g': 'Grabbing gold', 'c': 'Climbing up'}

        choices = list(actions.keys())

        if agent_type == 'naive':
            agent = NaiveAgent(choices)
        else:
            agent = HumanAgent(choices)

        action = None
        while True:
            percepts = self.environment.get_percepts(action)
            self.environment.print_grid()
            print(f"Observed: {percepts}")
            if self.debug:
                print(f"Current loc: {self.agent.location}")
                print(
                    f"facing: {self.agent.orientations[self.agent.orientation]}")
                print(f"Points: {self.agent.points()}")
            if self.agent.is_dead():
                self.environment.print_grid()
                print(
                    f"Agent died with {self.agent.points()} points")
                return

            if self.agent.exited():
                self.environment.print_grid()
                print(f"Agent exited with {self.agent.points()} points.")
                return True

            action = agent.next_step()
            print(f"{actions[action[0]]} ...")
