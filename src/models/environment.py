import numpy as np


class Room:
    has_stench = False
    has_breeze = False
    has_glitter = False
    has_wumpus = False

    def __init__(self, has_stench=False, has_breeze=False, has_glitter=False, has_wumpus=False, has_pit=False):
        self.has_stench = has_stench
        self.has_breeze = has_breeze
        self.has_glitter = has_glitter
        self.has_wumpus = has_wumpus
        self.has_pit = has_pit

    def put_wumpus(self):
        self.has_wumpus = True


class Environment:
    def __init__(self, width=4, height=4):
        self.gridHeight = height
        self.gridWidth = width

        self.pitProb = 0.2

        self.grid = np.empty((self.gridHeight, self.gridWidth), dtype=object)
        print(self.grid.shape)
        self.emptyRoom = Room()
        self.grid.fill(self.emptyRoom)

        self.pits = self._make_pits()
        for p in self.pits:
            self.grid.flat[p] = Room(has_pit=True)

            left = self.left_idx(p)
            if left > -1:
                self.set_breeze(left)

            right = self.right_idx(p)
            if right > -1:
                self.set_breeze(right)

            bottom = self.bottom_idx(p)
            if bottom > -1:
                self.set_breeze(bottom)

            top = self.top_idx(p)
            if top > -1:
                self.set_breeze(top)

        self.wumpus = self._make_wumpus()
        wumpus_loc = self.wumpus[0]
        self.set_wumpus(wumpus_loc)
        left = self.left_idx(wumpus_loc)
        if left > -1:
            self.set_stench(left)

        right = self.right_idx(wumpus_loc)
        if right > -1:
            self.set_stench(right)

        bottom = self.bottom_idx(wumpus_loc)
        if bottom > -1:
            self.set_stench(bottom)

        top = self.top_idx(wumpus_loc)
        if top > -1:
            self.set_stench(top)

        self.gold = self._make_gold()
        self.set_gold(self.gold[0])

    def set_wumpus(self, index):
        if (self.grid.flat[index] == self.emptyRoom):
            self.grid.flat[index] = Room(has_wumpus=True)
        else:
            self.grid.flat[index].has_wumpus = True

    def set_gold(self, index):
        if (self.grid.flat[index] == self.emptyRoom):
            self.grid.flat[index] = Room(has_glitter=True)
        else:
            self.grid.flat[index].has_glitter = True

    def set_breeze(self, index):
        if self.grid.flat[index] == self.emptyRoom:
            # create new room
            self.grid.flat[index] = Room(has_breeze=True)
        else:
            # update room element
            self.grid.flat[index].has_breeze = True

    def set_stench(self, index):
        if self.grid.flat[index] == self.emptyRoom:
            # create new room
            self.grid.flat[index] = Room(has_stench=True)
        else:
            # update room element
            self.grid.flat[index].has_stench = True

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
        print(self.pits, self.wumpus)
        print(self.grid)
        # Reverse range so 0,0 is at the bottom
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
                    element += 'B'
                if self.is_stench((i, j)):
                    element += 'S'
                row += ' ' * int(padding/2) + element + \
                    ' ' * (int(padding/2)-len(element)) + "|"
            print(row)
        print(("+" + "--------") * self.gridWidth + "+")
