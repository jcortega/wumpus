
import itertools
import operator
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

    _arrow_shot = False
    _wumpus_dead = False

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

    def _get_proba(self, model, observations, cell):
        X = torch.tensor([observations])

        X_masked = torch.masked.MaskedTensor(X, mask=X >= 0)
        prediction = model.predict_proba(X_masked)

        # Probability of X in given cell
        proba = prediction[self._cell_to_index(cell)]

        return proba.tolist()[0][1]

    def _get_wumpus_probable_loc(self):
        """
        Get the index and probability of most probable wumpus location
        """
        X = torch.tensor([self._wumpus_observations])

        X_masked = torch.masked.MaskedTensor(X, mask=X >= 0)
        prediction = self._wumpus_model.predict_proba(X_masked)

        # [x.tolist()[0][1] for x in prediction]
        # Probability of wumpus locations
        # print(list(enumerate(prediction[0:self.grid_size**2])))
        return max(enumerate(prediction[0:self.grid_size**2]), key=lambda x: x[1][0][1])

    def _get_dying_proba(self, loc):
        w_proba = self._get_proba(
            self._wumpus_model, self._wumpus_observations, loc)
        p_proba = self._get_proba(
            self._pit_model, self._pit_observations, loc)
        return w_proba + p_proba - w_proba * p_proba

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

    def _set_no_wumpus(self):
        self._wumpus_observations.fill(0)
        self._wumpus_dead = True

    def _set_no_wumpus_from(self, loc, orientation):
        """
        set locations where arrow passed in the orientation direction to 0
        orientation is orientation index
        """
        print(orientation, loc, "orrr")
        if orientation == 0:  # right
            for i in range(loc[1], self.grid_size):
                idx = self._cell_to_index((loc[0], i))
                self._wumpus_observations[idx] = 0
        elif orientation == 1:  # bottom
            for i in range(0, loc[0]):
                idx = self._cell_to_index((i, loc[1]))
                self._wumpus_observations[idx] = 0
        elif orientation == 2:  # left
            for i in range(0, loc[1]):
                idx = self._cell_to_index((loc[0], i))
                self._wumpus_observations[idx] = 0
        elif orientation == 3:  # up
            for i in range(loc[0], self.grid_size):
                idx = self._cell_to_index((i, loc[1]))
                self._wumpus_observations[idx] = 0

    def next_step(self, percepts=None):
        loc = self.agent_state.location
        orientation = self.agent_state.orientation
        self._set_breeze(loc, percepts["breeze"])
        self._set_stench(loc, percepts["stench"])

        agent_dead = self.agent_state.is_dead()
        self._set_safe(loc, agent_dead)

        if self._arrow_shot:
            if percepts["scream"]:
                self._set_no_wumpus()
            else:
                # if arrow shot but no scream, set arrow direction to wumpus=0
                self._set_no_wumpus_from(loc, orientation)

        if not self._wumpus_dead:
            probable_wumpus_loc = self._get_wumpus_probable_loc()
            print("Wumpus obs: ", self._wumpus_observations)
            print(
                f"Wumpus loc prob {probable_wumpus_loc[1][0][1]} at {probable_wumpus_loc[0]}")

        # print("Pit obs: ", self._pit_observations)
        print("Wumpus obs: ", self._wumpus_observations)

        # TODO: if risk of death is high on unvisited, move back
        # TODO: if prob of death > .5, find high prob of wumpus, shoot arrow or go home

        while True:
            adj_cells = self._get_surrounding_cell(
                loc[0], loc[1], self.grid_size)
            s = ""
            for i in adj_cells:
                s += f"{i} - Dying Prob: {self._get_dying_proba(i)};\n"

            print(f"{s}")
            action = input("Enter your action: ")
            if action not in self.choices:
                print("Invalid action. Try again...")
            else:
                if action == "s":
                    self._arrow_shot = True
                return action
