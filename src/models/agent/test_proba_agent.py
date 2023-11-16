import unittest

from .proba_agent import ProbaAgent
from ..environment import Environment, AgentState


class TestAiAssistedAgent(unittest.TestCase):
    def setUp(self):
        actions = {'f': 'Forward', 'l': 'TurnLeft',
                   'r': 'Turning Right', 's': 'Shooting wumpus', 'g': 'Grabbing gold', 'c': 'Climbing up'}
        # environment = Environment(
        # self.grid_width, self.gridth_height, True, self.pit_proba, debug=debug)
        agent_state = AgentState()
        self.agent = ProbaAgent(
            list(actions.keys()), agent_state, 4, .2)

    def test__path_to_actions(self):
        """
        without after action
        """
        path = [((2, 0), 3), ((2, 0), 0), ((2, 0), 1),
                ((1, 0), 1), ((1, 0), 0), ((1, 1), 0)]
        expected = ['r', 'r', 'f', 'l', 'f']
        result = self.agent._path_to_actions(path)
        self.assertEqual(expected, result)

    def test__path_to_actions_with_after(self):
        """
        with after action
        """
        path = [((2, 0), 3), ((2, 0), 0), ((2, 0), 1),
                ((1, 0), 1), ((1, 0), 0), ((1, 1), 0)]
        expected = ['r', 'r', 'f', 'l', 'f', 'c']
        result = self.agent._path_to_actions(path, ['c'])
        self.assertEqual(expected, result)

    def test__cell_to_index(self):
        res = self.agent._cell_to_index((3, 3))
        self.assertEqual(res, 15)

    def test__index_to_cell(self):
        res = self.agent._index_to_cell(15)
        self.assertEqual(res, (3, 3))

    def test__get_relative_orientation_of(self):
        from_cell = (2, 2)
        of_cell = (3, 2)
        expected = 3  # top
        res = self.agent._get_relative_orientation_of(of_cell, from_cell)
        self.assertEqual(res, expected)

        # More than 1 spaces
        from_cell = (1, 2)
        of_cell = (3, 2)
        expected = 3  # top
        res = self.agent._get_relative_orientation_of(of_cell, from_cell)

        from_cell = (3, 3)
        of_cell = (3, 2)
        expected = 2  # left
        res = self.agent._get_relative_orientation_of(of_cell, from_cell)

        from_cell = (3, 2)
        of_cell = (3, 3)
        expected = 0  # right
        res = self.agent._get_relative_orientation_of(of_cell, from_cell)

        from_cell = (3, 3)
        of_cell = (2, 3)
        expected = 1  # bottom
        res = self.agent._get_relative_orientation_of(of_cell, from_cell)

        self.assertEqual(res, expected)
