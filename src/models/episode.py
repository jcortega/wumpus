import time
import numpy as np

from .environment import Environment
from .agent.naive_agent import NaiveAgent
from .agent.human_agent import HumanAgent
from .agent.proba_agent import ProbaAgent
from .agent.move_planning_agent import MovePlanningAgent


class Episode:
    def __init__(self, debug):
        self.debug = debug
        self.grid_width = 4
        self.gridth_height = self.grid_width
        self.pit_proba = 0.2
        self.environment = Environment(
            self.grid_width, self.gridth_height, True, self.pit_proba, debug=debug)
        self.agent_state = self.environment.get_agent_state()

        self.oldloc = (0, 0)
        self.loc = (0, 0)
        self.orientation_idx = 0
        self.points = 0
        self.grabbed_gold = False

    def run(self, agent_type='naive'):
        print(f"Running episode with {agent_type} agent...")

        actions = {'f': 'Forward', 'l': 'TurnLeft',
                   'r': 'Turning Right', 's': 'Shooting wumpus', 'g': 'Grabbing gold', 'c': 'Climbing up'}

        if agent_type == 'naive':
            choices = ['f', 'l', 'r', 's', 'g', 'c']
            agent = NaiveAgent(choices)
        elif agent_type == 'move_planning':
            choices = ['f', 'l', 'r', 's']  # remove grab and climb
            agent = MovePlanningAgent(choices, self.agent_state)
        elif agent_type == 'proba_agent':
            agent = ProbaAgent(
                list(actions.keys()), self.agent_state, self.grid_width, self.pit_proba)
        else:
            agent = HumanAgent(list(actions.keys()))

        action = None
        while True:
            percepts = self.environment.get_percepts(action)
            self.environment.print_grid()
            print(f"Observed: {percepts}")
            if self.debug:
                print(f"Current loc: {self.agent_state.location}")
                print(
                    f"facing: {self.agent_state.orientations[self.agent_state.orientation]}")
                print(f"Points: {self.agent_state.points()}")
            if self.agent_state.is_dead():
                self.environment.print_grid()
                print(
                    f"Agent died with {self.agent_state.points()} points")
                return self.agent_state.points()

            if self.agent_state.exited():
                self.environment.print_grid()
                print(f"Agent exited with {self.agent_state.points()} points.")
                return self.agent_state.points()

            action = agent.next_step(percepts)[0]
            print(f"{actions[action[0]]} ...")
