import numpy as np


class Room:
    has_stench = False
    has_breeze = False
    has_glitter = False
    has_wumpus = False
    has_pit = False

    def __init__(self, has_stench=False, has_breeze=False, has_glitter=False, has_wumpus=False, has_pit=False):
        self.has_stench = has_stench
        self.has_breeze = has_breeze
        self.has_glitter = has_glitter
        self.has_wumpus = has_wumpus
        self.has_pit = has_pit


class Environment:
    def __init__(self, width=4, height=4):
        self.gridHeight = height
        self.gridWidth = width

        self.pitProb = 0.2

        self.grid = self.__init_empty_grid()

        pits = self._make_pits()
        for p in pits:
            self.grid.flat[p].has_pit = True

            left = self.left_idx(p)
            if left > -1:
                self.grid.flat[left].has_breeze = True

            right = self.right_idx(p)
            if right > -1:
                self.grid.flat[right].has_breeze = True

            bottom = self.bottom_idx(p)
            if bottom > -1:
                self.grid.flat[bottom].has_breeze = True

            top = self.top_idx(p)
            if top > -1:
                self.grid.flat[top].has_breeze = True

        wumpus = self._make_wumpus()
        wumpus_loc = wumpus[0]
        self.grid.flat[wumpus_loc].has_wumpus = True

        left = self.left_idx(wumpus_loc)
        if left > -1:
            self.grid.flat[left].has_stench = True

        right = self.right_idx(wumpus_loc)
        if right > -1:
            self.grid.flat[right].has_stench = True

        bottom = self.bottom_idx(wumpus_loc)
        if bottom > -1:
            self.grid.flat[bottom].has_stench = True

        top = self.top_idx(wumpus_loc)
        if top > -1:
            self.grid.flat[top].has_stench = True

        gold = self._make_gold()
        self.grid.flat[gold[0]].has_glitter = True

    def __init_empty_grid(self):
        grid = np.empty((self.gridHeight, self.gridWidth), dtype=object)
        for i in range(0, self.gridHeight):
            for j in range(0, self.gridWidth):
                grid[i, j] = Room()
        return grid

    def right_idx(self, index):
        # returns flat index next to index if exists
        right = index + 1
        if (right % self.gridWidth) == 0:
            return -1
        return right

    def left_idx(self, index):
        # returns flat index next to index if exists
        if (index % self.gridWidth) == 0:
            return -1
        return index - 1

    def top_idx(self, index):
        """
        returns flat index to the top of the given index if exists
        """
        top = index + self.gridWidth
        if (top > self.gridHeight * self.gridWidth - 1):
            return -1
        return top

    def bottom_idx(self, index):
        """
        returns flat index to the bottom of the givenindex if exists
        """
        bottom = index - self.gridWidth
        if (bottom < 0):
            return -1
        return bottom

    def pit_count(self):
        return int(self.pitProb * (self.gridHeight * self.gridWidth - 1))

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
        return self.grid.item(index).has_pit

    def is_wumpus(self, index):
        return self.grid.item(index).has_wumpus

    def is_gold(self, index):
        return self.grid.item(index).has_glitter

    def is_breeze(self, index):
        return self.grid.item(index).has_breeze

    def is_stench(self, index):
        return self.grid.item(index).has_stench

    def print_grid(self):
        # Reverse range so 0,0 is at the bottom
        print("\n")
        for i in reversed(range(self.gridHeight)):
            padding = 8
            print(("+" + "-" * padding) * self.gridWidth + "+")
            row = "|"
            for j in range(self.gridWidth):
                # item = self.grid.item((i, j))
                element = ''
                if self.is_pit((i, j)):
                    element += 'P'
                if self.is_wumpus((i, j)):
                    element += 'W'
                if self.is_gold((i, j)):
                    element += 'G'
                if self.is_breeze((i, j)):
                    element += 'b'
                if self.is_stench((i, j)):
                    element += 's'
                row += ' ' * int(padding/2) + element + \
                    ' ' * (int(padding/2)-len(element)) + "|"
            print(row)
        print(("+" + "-" * padding) * self.gridWidth + "+")
