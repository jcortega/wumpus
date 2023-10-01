import unittest

from environment import Environment


class TestSquareEnvironment(unittest.TestCase):
    def setUp(self):
        self.environment = Environment(width=5, height=4)

    def test_print_grid(self):
        self.environment.print_grid()

    def test_right_idx(self):
        i = self.environment.right_idx(4)
        self.assertEqual(i, -1)

        i = self.environment.right_idx(13)
        self.assertEqual(i, 14)

        i = self.environment.right_idx(5)
        self.assertEqual(i, 6)

        i = self.environment.right_idx(19)
        self.assertEqual(i, -1)

    def test_left_idx(self):
        i = self.environment.left_idx(4)
        self.assertEqual(i, 3)

        i = self.environment.left_idx(13)
        self.assertEqual(i, 12)

        i = self.environment.left_idx(5)
        self.assertEqual(i, -1)

        i = self.environment.left_idx(19)
        self.assertEqual(i, 18)

    def test_top_idx(self):
        i = self.environment.top_idx(4)
        self.assertEqual(i, 9)

        i = self.environment.top_idx(13)
        self.assertEqual(i, 18)

        i = self.environment.top_idx(5)
        self.assertEqual(i, 10)

        i = self.environment.top_idx(19)
        self.assertEqual(i, -1)

    def test_bottom_idx(self):
        i = self.environment.bottom_idx(4)
        self.assertEqual(i, -1)

        i = self.environment.bottom_idx(13)
        self.assertEqual(i, 8)

        i = self.environment.bottom_idx(5)
        self.assertEqual(i, 0)

        i = self.environment.bottom_idx(19)
        self.assertEqual(i, 14)


if __name__ == '__main__':
    unittest.main()
