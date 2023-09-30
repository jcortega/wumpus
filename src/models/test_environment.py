import unittest

from environment import Environment


class TestEnvironment(unittest.TestCase):
    def setUp(self):
        self.environment = Environment()

    def test_print_grid(self):
        self.environment._make_pits()
        self.environment.print_grid()


if __name__ == '__main__':
    unittest.main()
