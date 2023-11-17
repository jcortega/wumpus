
import itertools
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

from pomegranate.distributions import Categorical
from pomegranate.distributions import ConditionalCategorical
from pomegranate.bayesian_network import BayesianNetwork
import torch


class ProbaAgent:
    choices = []

    _pit_model = BayesianNetwork()
    _pit_observations = []

    _wumpus_model = BayesianNetwork()
    _wumpus_observations = []

    _node_length = None

    _arrow_shot = False
    _wumpus_dead = False

    _path = nx.DiGraph()

    _planned_action = []  # Planned action for going to recommended destination

    agent_state = None

    def __init__(self, choices, agent_state, grid_size, pit_proba):
        # Clear graph to make sure no nodes in graph
        # Found a bug in networkx that initializes graph with several nodes already in it
        self._path.clear()

        print("Initial path nodes on initialization: ", self._path.nodes())

        self.choices = choices
        self.grid_size = grid_size
        self.agent_state = agent_state
        print(
            f"Initial Arrows: {self.agent_state.arrows} WumpDead: {self._wumpus_dead}")

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

    def _visualize_graph(self):
        plt.figure().clear()
        plt.subplot()
        nx.draw(self._path, with_labels=True, font_size=8, linewidths=0.5)
        plt.savefig('proba_agent_path_graph.png')

    def _manhattan_dist(self, a, b):
        ((x1, y1), _) = a
        ((x2, y2), _) = b
        return ((x1 - x2) + (y1 - y2))

    def _cell_to_index(self, cell):
        """
        2D coordinate to flat index
        """
        return cell[0]*self.grid_size + cell[1]

    def _index_to_cell(self, index):
        """
        Flat index to 2D coordinate
        """
        return (index//self.grid_size, index % self.grid_size)

    def _get_surrounding_cell(self, col, row, grid_size):
        cells = []

        if row + 1 < grid_size:
            # top
            cells.append((row+1, col))
        if col + 1 < grid_size:
            # Right
            cells.append((row, col + 1))
        if row - 1 >= 0:
            # bottom
            cells.append((row - 1, col))

        if col - 1 >= 0:
            # Left
            cells.append((row, col - 1))

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
                    col, row, self.grid_size)
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
                    col, row, self.grid_size)
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
        if self._wumpus_dead:
            print("Calculating proba without wumpus..")
            return self._get_proba(
                self._pit_model, self._pit_observations, loc)
        else:
            print("Calculating proba with wumpus..")
            w_proba = self._get_proba(
                self._wumpus_model, self._wumpus_observations, loc)
            p_proba = self._get_proba(
                self._pit_model, self._pit_observations, loc)
            print(f"{w_proba} {p_proba}  {w_proba * p_proba}")
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

    def _get_relative_orientation_of(self, cell, from_cell):
        diff = (cell[0] - from_cell[0], cell[1] - from_cell[1])
        if cell == from_cell:
            return -1  # same point
        elif diff[0] > 0:
            return 3  # 'top'
        elif diff[0] < 0:
            return 1  # 'bottom'
        elif diff[1] > 0:
            return 0  # 'right'
        elif diff[1] < 0:
            return 2  # 'left'
        else:
            # Probably not line of sight
            return -2

    def _add_node_to_path(self, loc, orientation):
        adj_cells = self._get_surrounding_cell(loc[1], loc[0], self.grid_size)
        print("Add node to path call():")
        print("---", adj_cells)
        print("---", loc)

        for i in adj_cells:
            # Relative orientation of i from loc with proba of dying as weight
            rel_orientation = self._get_relative_orientation_of(i, loc)
            # self._path.add_node((i, rel_orientation))
            self._path.add_edge((loc, rel_orientation),
                                (i, rel_orientation))

            # Add turn paths (no risk of dying)
            for j in range(4):
                self._path.add_edge((loc, j), (loc, (j+1) % 4))
                self._path.add_edge((loc, j), (loc, (j-1) % 4))

        # For debugging purposes
        # self._visualize_graph()

    def _get_leaf_nodes(self):
        print("Path nodes: ", self._path.nodes())
        return [node for node in self._path.nodes()
                if self._path.in_degree(node) != 0 and self._path.out_degree(node) == 0]

    def _get_least_proba_dying_nodes(self, leaf_nodes):
        """
        Given leaf nodes, return nodes with least probability of dying
        """
        # NOTE: This could be optimized by calling dying proba prediction for all nodes in one calls
        dying_proba = [self._get_dying_proba(node[0]) for node in leaf_nodes]
        least_proba = min(dying_proba)

        probabilities = (least_proba, [leaf_nodes[k] for k, v in enumerate(dying_proba)
                                       if least_proba == v])
        print("Probabilities of dying per node: ", dying_proba)
        print("Leaf Nodes: ", leaf_nodes)
        return probabilities

    def _get_shortest_path(self, from_loc, nodes):
        min = None
        min_path = None
        for node in nodes:
            path = self._get_shortest_path_to_node(from_loc, node)
            if min == None or min > len(path):
                min = len(path)
                min_path = path

        return min, min_path

    def _get_shortest_path_to_node(self, from_loc, node):
        return nx.astar_path(self._path, from_loc, node, heuristic=self._manhattan_dist)

    def _get_home_path(self, from_loc):
        min_path = None
        min_path_cost = None
        for i in range(4):
            path = nx.astar_path(self._path, from_loc, ((0, 0), i),
                                 heuristic=self._manhattan_dist)
            if min_path == None or len(path) < min_path_cost:
                min_path_cost = len(path)
                min_path = path

        return min_path

    def _path_to_actions(self, path, after=[]):
        """
        Convert path, as returned by networkx, to actions
        Assumes that the first element is the current location
        """
        actions = []
        loc = path.pop(0)  # (coord_loc, orientation)
        for next_node in path:
            if next_node[0] != loc[0]:
                # next action is forward if coordinates not the same
                actions.append('f')
            else:
                # Else turn
                diff = next_node[1] - loc[1]
                if diff == 1 or diff == -3:
                    # positive diff means turn right
                    actions.append('r')
                elif diff == -1 or diff == 3:
                    actions.append('l')
            loc = next_node

        return actions + after

    def next_step(self, percepts=None):
        loc = self.agent_state.location
        orientation = self.agent_state.orientation

        # Execute planned action before calculating new actions
        if self._planned_action:
            action = self._planned_action.pop(0)
            print(f"Executing planned action.. {action}")

            if action == 's':
                self._arrow_shot = True

            return action

        # Set breeze or stench if found
        self._set_breeze(loc, percepts["breeze"])
        self._set_stench(loc, percepts["stench"])

        agent_dead = self.agent_state.is_dead()

        # Set node to be safe if agent did not die, probably unnecessary step
        self._set_safe(loc, agent_dead)

        self._add_node_to_path(loc, orientation)
        leaf_nodes = self._get_leaf_nodes()
        print("Leaf nodes:", leaf_nodes)
        if self._arrow_shot:
            if percepts["scream"]:
                print("setting wumpus to dead")
                self._set_no_wumpus()
            else:
                # if arrow shot but no scream, set arrow direction to wumpus=0
                self._set_no_wumpus_from(loc, orientation)
            self._arrow_shot = False  # Reset arrow shot indicator

        # Recommendation calculation
        if percepts["glitter"]:
            print("Recommendation: grab and go home")
            # reset planned path if any and go home
            home_path = self._get_home_path((loc, orientation))
            print("home_path", home_path)
            self._planned_action = self._path_to_actions(home_path, ['c'])
            return 'g'
        elif percepts["stench"] and self.agent_state.arrows >= 1 and not self._wumpus_dead:
            # Constraint (c) give up without attempting to kill the Wumpus if it is likely to be beneficial
            # Constraint (d) waste its arrow unnecessarily
            print("Recommendation: find wump and shoot")
            if not self._wumpus_dead:
                probable_wumpus_loc_idx, wumpus_proba = self._get_wumpus_probable_loc()
                probable_wumpus_loc_cell = self._index_to_cell(
                    probable_wumpus_loc_idx)
                probable_wumpus_rel_orientation = self._get_relative_orientation_of(
                    probable_wumpus_loc_cell, loc)
                print(
                    f"Wumpus loc prob {wumpus_proba} at {probable_wumpus_loc_cell} direction {probable_wumpus_rel_orientation}")
                if probable_wumpus_rel_orientation == orientation:
                    # agent already line of sight, shoot now
                    self._arrow_shot = True
                    return 's'
                elif probable_wumpus_rel_orientation > 0:
                    # wumpus is in line of sight but different direction
                    # just make some turns
                    rotation_path = self._get_shortest_path_to_node(
                        (loc, orientation), (loc, probable_wumpus_rel_orientation))
                    self._planned_action = self._path_to_actions(
                        rotation_path, ['s'])
                    return self._planned_action.pop(0)

                # Else, not line of sight, dont waste arrow and move on

        # Constraint (a) unnecessarily visit locations it’s already been
        # If no stench or glitter, find cell least probability of dying
        least_dying_proba, min_dying_nodes = self._get_least_proba_dying_nodes(
            leaf_nodes)
        print("Minimum", least_dying_proba, min_dying_nodes)

        # Constraint (b) take unnecessary risks
        # Constraint (e) to give up unless the next move is more than 50%
        if least_dying_proba > 0.5:
            print("Recommendation: go home")
            if loc == (0, 0):
                return 'c'
            else:
                home_path = self._get_home_path((loc, orientation))
                print("home_path", home_path)
                self._planned_action = self._path_to_actions(
                    home_path, ['c'])
                return self._planned_action.pop(0)
        else:
            # returns cost, path
            shortest_path = self._get_shortest_path(
                (loc, orientation), min_dying_nodes)
            print(
                f"Minimum path steps:{shortest_path[0]}; path: {shortest_path[1]}")
            print(f"Recommendation: go to {shortest_path[1][-1]}")

            self._planned_action = self._path_to_actions(shortest_path[1])
            return self._planned_action.pop(0)
