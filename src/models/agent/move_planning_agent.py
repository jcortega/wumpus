from copy import deepcopy
import sys
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


class MovePlanningAgent:
    _choices = []
    _has_gold = False
    _previous_loc = (0, 0)
    _previous_orientation = 0  # right
    _previous_action = None
    _planned_actions = None

    G = nx.DiGraph()

    def __init__(self, choices, agent_state):
        self.agent_state = agent_state
        self._choices = choices

        self._add_common_edge((0, 0))

    def _plan_move_back(self, loc, orientation):
        from_node = (loc[0], loc[1],
                     self.agent_state.orientations[orientation])

        path = None
        for d in self.agent_state.orientations:
            to_node = (0, 0, d)
            new_path = nx.astar_path(self.G, from_node, to_node,
                                     heuristic=self._manhattan_dist)

            if path == None or len(new_path) < len(path):
                path = deepcopy(new_path)

        return path

    def _add_common_edge(self, node):
        self.G.add_edge((node[0], node[1], 'right'),
                        (node[0], node[1], 'down'), action='r')
        self.G.add_edge((node[0], node[1], 'down'),
                        (node[0], node[1], 'left'), action='r')
        self.G.add_edge((node[0], node[1], 'left'),
                        (node[0], node[1], 'up'), action='r')
        self.G.add_edge((node[0], node[1], 'up'),
                        (node[0], node[1], 'right'), action='r')

        self.G.add_edge((node[0], node[1], 'right'),
                        (node[0], node[1], 'up'), action='l')
        self.G.add_edge((node[0], node[1], 'down'),
                        (node[0], node[1], 'right'), action='l')
        self.G.add_edge((node[0], node[1], 'left'),
                        (node[0], node[1], 'down'), action='l')
        self.G.add_edge((node[0], node[1], 'up'),
                        (node[0], node[1], 'left'), action='l')

    def _manhattan_dist(self, a, b):
        (x1, y1, *rest) = a
        (x2, y2, *rest) = b
        return ((x1 - x2) + (y1 - y2))

    def _calculate_next_actions(self, path):
        next_actions = []

        node1 = path.pop(0)
        node2 = None
        while path:
            node2 = path.pop(0)
            if node1[2] == node2[2]:
                next_actions.append('f')
            elif node1[2] == 'down':
                if node2[2] == 'left':
                    next_actions.append('r')
                elif node2[2] == 'right':
                    next_actions.append('l')
            elif node1[2] == 'up':
                if node2[2] == 'left':
                    next_actions.append('l')
                elif node2[2] == 'right':
                    next_actions.append('r')
            elif node1[2] == 'left':
                if node2[2] == 'down':
                    next_actions.append('l')
                elif node2[2] == 'up':
                    next_actions.append('r')
            elif node1[2] == 'right':
                if node2[2] == 'down':
                    next_actions.append('r')
                elif node2[2] == 'up':
                    next_actions.append('l')
            node1 = node2
        return next_actions

    def _visualize_graph(self):
        plt.figure().clear()
        plt.subplot()
        nx.draw(self.G, with_labels=True, font_size=8, linewidths=0.5)
        plt.savefig('move_planning_graph.png')

    def next_step(self, percepts):
        if self._planned_actions:
            next = self._planned_actions.pop(0)
            return [next]

        if self._has_gold:
            if self.agent_state.location == (0, 0):
                return ['c']

        # Build graph
        if self.agent_state.location != self._previous_loc:
            opposite_orientation = (self._previous_orientation + 2) % 4
            self.G.add_edge((self.agent_state.location[0], self.agent_state.location[1], self.agent_state.orientations[opposite_orientation]),
                            (self._previous_loc[0], self._previous_loc[1],  self.agent_state.orientations[opposite_orientation]), action='f')

            # Top
            if self.G.has_node((self.agent_state.location[0]+1, self.agent_state.location[1], 'down')):
                self.G.add_edge((self.agent_state.location[0]+1, self.agent_state.location[1], 'down'), (self.agent_state.location[0], self.agent_state.location[
                                1], 'down'), action='f')
            if self.G.has_node((self.agent_state.location[0]+1, self.agent_state.location[1], 'up')):
                self.G.add_edge((self.agent_state.location[0], self.agent_state.location[1], 'up'), (
                    self.agent_state.location[0]+1, self.agent_state.location[1], 'up'), action='f')

            # bottom
            if self.G.has_node((self.agent_state.location[0]-1, self.agent_state.location[1], 'up')):
                self.G.add_edge((self.agent_state.location[0]-1, self.agent_state.location[1], 'up'), (self.agent_state.location[0], self.agent_state.location[
                                1], 'up'), action='f')
            if self.G.has_node((self.agent_state.location[0]-1, self.agent_state.location[1], 'down')):
                self.G.add_edge((self.agent_state.location[0], self.agent_state.location[1], 'down'), (
                    self.agent_state.location[0]-1, self.agent_state.location[1], 'down'), action='f')

            # left
            if self.G.has_node((self.agent_state.location[0], self.agent_state.location[1]-1, 'right')):
                self.G.add_edge((self.agent_state.location[0], self.agent_state.location[1]-1, 'right'), (self.agent_state.location[0], self.agent_state.location[
                                1], 'right'), action='f')
            if self.G.has_node((self.agent_state.location[0], self.agent_state.location[1]-1, 'left')):
                self.G.add_edge((self.agent_state.location[0], self.agent_state.location[1], 'left'), (
                    self.agent_state.location[0], self.agent_state.location[1]-1, 'left'), action='f')

            # right
            if self.G.has_node((self.agent_state.location[0], self.agent_state.location[1]+1, 'left')):
                self.G.add_edge((self.agent_state.location[0], self.agent_state.location[1]+1, 'left'), (self.agent_state.location[0], self.agent_state.location[
                                1], 'left'), action='f')
            if self.G.has_node((self.agent_state.location[0], self.agent_state.location[1]+1, 'right')):
                self.G.add_edge((self.agent_state.location[0], self.agent_state.location[1], 'right'), (
                    self.agent_state.location[0], self.agent_state.location[1]+1, 'right'), action='f')

            self._add_common_edge(self.agent_state.location)

        if percepts['glitter']:
            self._has_gold = True

            path = self._plan_move_back(self.agent_state.location,
                                        self.agent_state.orientation)

            if path[0] != (*self.agent_state.location, self.agent_state.orientations[self.agent_state.orientation]):
                raise Exception(
                    "First node of path is not current location and orientation")

            self._planned_actions = self._calculate_next_actions(path)

            return ['g']

        self._previous_loc = deepcopy(self.agent_state.location)
        self._previous_orientation = self.agent_state.orientation
        self._previous_action = np.random.choice(self._choices, 1)

        return self._previous_action
