import numpy as np


class Environment:
    def __init__(self):
        self.pitProb = 0.2
        self.gridSize = 4
        self.grid = np.random.randint(0, 15, (self.gridSize, self.gridSize))

        self.pits = self._make_pits()
        self.wumpus = self._make_wumpus()
        self.gold = self._make_gold()

    def pit_count(self):
        return int(self.pitProb * (self.gridSize * self.gridSize - 1))

    def _make_pits(self):
        cellsChoices = np.arange(1, self.grid.size)
        pitCount = self.pit_count()
        return np.random.choice(cellsChoices, pitCount, replace=False)

    def _make_wumpus(self):
        cellsChoices = np.arange(1, self.grid.size)
        cellsChoices = np.setdiff1d(cellsChoices, self.pits)
        return np.random.choice(cellsChoices, 1, replace=False)

    def _make_gold(self):
        cellsChoices = np.arange(1, self.grid.size)
        cellsChoices = np.setdiff1d(cellsChoices, self.pits)
        cellsChoices = np.setdiff1d(cellsChoices, self.wumpus)
        return np.random.choice(cellsChoices, 1, replace=False)

    def is_pit(self, index):
        flatIndex = index[0]*self.gridSize+index[1]
        # print(flatIndex, index, self.pits)
        return flatIndex in self.pits

    def is_wumpus(self, index):
        flatIndex = index[0]*self.gridSize+index[1]
        # print(flatIndex, index, self.pits)
        return flatIndex in self.wumpus

    def is_gold(self, index):
        flatIndex = index[0]*self.gridSize+index[1]
        # print(flatIndex, index, self.pits)
        return flatIndex in self.gold

    def print_grid(self, area=4):
        print(self.pits, self.wumpus)
        size = self.gridSize
        # Reverse range so 0,0 is at the bottom
        for i in reversed(range(size)):
            print(("+" + "- " * area) * size + "+")
            row = "|"
            for j in range(area):
                # item = self.grid.item((i, j))
                element = ' '
                if self.is_pit((i, j)):
                    element = 'P'
                elif self.is_wumpus((i, j)):
                    element = 'W'
                elif self.is_gold((i, j)):
                    element = 'G'
                row += f"   {element}    |"
            print(row)
        print(("+" + "- " * area) * size + "+")
