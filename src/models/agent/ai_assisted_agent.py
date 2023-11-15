
import itertools
import numpy as np
import pandas as pd

from pomegranate.distributions import Categorical
from pomegranate.distributions import ConditionalCategorical
from pomegranate.bayesian_network import BayesianNetwork
import torch


class AiAssistedAgent:
    choices = []

    _pit_model = BayesianNetwork()
    _pit_observations = []
    
    _wumpus_model = BayesianNetwork()
    _wumpus_observations = []

    _node_length = None

    agent_state = None

    def __init__(self, choices, agent_state, grid_size, pit_proba):
        self.choices = choices
        self.grid_size = grid_size
        self.agent_state = agent_state

        print("Initializing models...")
        self._pit_model = self._init_pit_model(pit_proba)
        self._wumpus_model = self._init_wumpus_model()

        # x4 assuming square, x2 for pit and breeze
        self._node_length = self.grid_size*4*2

        # initialize pit observation to -1 (unknown)
        self._pit_observations = np.arange(self._node_length)
        self._pit_observations.fill(-1)

        # initialize wumpus observation to -1 (unknown)
        self._wumpus_observations = np.arange(self._node_length)
        self._wumpus_observations.fill(-1)

        # Position 0 has no pit and wumpus
        self._pit_observations[0] = 0
        self._wumpus_observations[0] = 0

        # TODO: need observation for wumpus

    def _cell_to_index(self, cell):
        return cell[0]*self.grid_size + cell[1]

    def _get_surrounding_cell(self, col, row, grid_size):
        cells = []

        if row + 1 < grid_size:
            # top
            cells.append((col, row+1))
        if col + 1 < grid_size:
            # Right
            cells.append((col + 1, row))
        if row - 1 >= 0:
            # bottom
            cells.append((col, row - 1))

        if col - 1 >= 0:
            # Left
            cells.append((col - 1, row))

        return cells

    def _transform_distribution(self, dist):
        """
        Transform distribution to pomegranate distribution structure
        """
        mid = len(dist)//2
        dist = [dist[:mid], dist[mid:]]

        if len(dist[0]) > 2:
            dist[0] = self._transform_distribution(dist[0])
        if len(dist[1]) > 2:
            dist[1] = self._transform_distribution(dist[1])
        return dist

    def _init_wumpus_model(self):
        wumpus_model = BayesianNetwork()

        wumpus_prob_dists = {}
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                wumpus_prob_dists[(row, col)] = Categorical(
                    [[1-1/self.grid_size, 1/self.grid_size]])
                wumpus_model.add_distribution(wumpus_prob_dists[(row, col)])

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                adjacent_cells = self._get_surrounding_cell(
                    row, col, self.grid_size)
                table = list(itertools.product(
                    [False, True], repeat=len(adjacent_cells)+1))
                df = pd.DataFrame(table, columns=adjacent_cells + ['stench'])
                df['any'] = df.apply(lambda x: any(x[adjacent_cells]), axis=1)
                df['prob'] = df.apply(lambda x: 1.0 if x['any'] ==
                                      x['stench'] else 0.0, axis=1)
                stench_dist = ConditionalCategorical(
                    [self._transform_distribution(df['prob'].tolist())])
                wumpus_model.add_distribution(stench_dist)

                for adj in adjacent_cells:
                    wumpus_model.add_edge(
                        wumpus_prob_dists[adj], stench_dist)

        return wumpus_model

    def _init_pit_model(self, proba):
        pit_model = BayesianNetwork()

        pit_prob_dists = {}
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                pit_prob_dists[(row, col)] = Categorical([[1-proba, proba]])
                pit_model.add_distribution(pit_prob_dists[(row, col)])

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                adjacent_cells = self._get_surrounding_cell(
                    row, col, self.grid_size)
                table = list(itertools.product(
                    [False, True], repeat=len(adjacent_cells)+1))
                df = pd.DataFrame(table, columns=adjacent_cells + ['breeze'])
                df['any'] = df.apply(lambda x: any(x[adjacent_cells]), axis=1)
                df['prob'] = df.apply(lambda x: 1.0 if x['any'] ==
                                      x['breeze'] else 0.0, axis=1)
                breeze_dist = ConditionalCategorical(
                    [self._transform_distribution(df['prob'].tolist())])
                pit_model.add_distribution(breeze_dist)

                for adj in adjacent_cells:
                    pit_model.add_edge(
                        pit_prob_dists[adj], breeze_dist)

        return pit_model

    def _get_pit_proba(self, model, cell):
        X = torch.tensor([self._pit_observations])

        X_masked = torch.masked.MaskedTensor(X, mask=X >= 0)
        prediction = model.predict_proba(X_masked)

        # Probability of pit in given cell
        proba = prediction[self._cell_to_index(cell)]
        return proba.tolist()[0][1]

    def _set_breeze(self, loc, value):
        idx = self._cell_to_index(loc)

        # order of array is [pit_probs ... breeze_probs] so 16 + idx is breeze probs
        self._pit_observations[16+idx] = 1.0 if value else 0.0

    def _set_stench(self, loc, value):
        idx = self._cell_to_index(loc)

        # order of array is [pit_probs ... stench_probs] so 16 + idx is stench probs
        self._wumpus_observations[16+idx] = 1.0 if value else 0.0

    def _set_safe(self, loc, value):
        idx = self._cell_to_index(loc)

        # order of array is [pit_probs ... breeze_probs] so idx is pit probs
        self._pit_observations[idx] = 0.0

        # order of array is [wumpus_probs ... stench_probs] so idx is pit probs
        self._wumpus_observations[idx] = 0.0


    def next_step(self, percepts=None):
        print("From next", percepts)
        loc = self.agent_state.location
        self._set_breeze(loc, percepts["breeze"])
        self._set_stench(loc, percepts["stench"])

        agent_dead = self.agent_state.is_dead()
        self._set_safe(loc, agent_dead)

        print("Pit obs: ", self._pit_observations)
        print("Wumpus obs: ", self._wumpus_observations)

        while True:
            adj_cells = self._get_surrounding_cell(
                loc[0], loc[1], self.grid_size)
            s = ""
            for i in adj_cells:
                s += f"Adjacent cell {i}: {self._get_pit_proba(self._pit_model, i)}; "

            print(f"{s}")
            action = input("Enter your action: ")
            if action not in self.choices:
                print("Invalid action. Try again...")
            else:
                return action
