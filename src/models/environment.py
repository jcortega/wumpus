import numpy as np

from .agent import Agent

from .room import Room


class Environment:
    def __init__(self, width=4, height=4, allowClimbWithoutGold=False, pitProb=0.2, debug=False):
        self.Agent = None
        self.gridHeight = height
        self.gridWidth = width
        self.allowClimbWithoutGold = allowClimbWithoutGold
        self.pitProb = pitProb

        self._debug = debug

        self.wumpus_dead = False
        self.gold_grabbed = False

        self.__set_environment()

    def __set_environment(self):
        self.grid = self.__init_empty_grid()

        pits = self._draw_room(self.pit_count(), [])
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

        wumpus = self._draw_room(1, pits)
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

        gold = self._draw_room(1, np.append(pits, wumpus))

        self.grid.flat[gold[0]].has_glitter = True

        self.grid[0, 0].visited = True

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

    def _draw_room(self, count, exclude=[]):
        choices = np.arange(1, self.grid.size)
        choices = np.setdiff1d(choices, exclude)
        return np.random.choice(choices, count, replace=False)

    def _is_pit(self, index):
        return self.grid.item(index).has_pit

    def _is_wumpus(self, index):
        return self.grid.item(index).has_wumpus

    def _is_gold(self, index):
        return self.grid.item(index).has_glitter

    def _is_breeze(self, index):
        return self.grid.item(index).has_breeze

    def _is_stench(self, index):
        return self.grid.item(index).has_stench

    def _get_next_loc(self, location, orientation):
        if (orientation == 0):  # Right
            return (location[0], location[1]+1)
        elif (orientation == 2):  # left
            return (location[0], location[1]-1)
        elif (orientation == 3):  # right
            return (location[0]+1, location[1])
        elif (orientation == 1):  # down
            return (location[0]-1, location[1])

    def _will_hit_wall(self, location):
        return location[0] >= self.gridHeight or location[0] < 0 or \
            location[1] >= self.gridWidth or location[1] < 0

    def _shoot_wumpus(self, from_loc, direction):
        if self.agent.arrows <= 0:
            print("No more arrows...")
            return False

        self.agent.arrows -= 1
        if direction == 'left':
            for n in reversed(range(0, from_loc[1])):
                room = self.grid.item((from_loc[0], n))
                if room.has_wumpus:
                    self.wumpus_dead = True
                    self.room_has_humpus = False
                    return True

        elif direction == 'right':
            for n in range(from_loc[1], self.gridWidth):
                room = self.grid.item((from_loc[0], n))
                if room.has_wumpus:
                    self.wumpus_dead = True
                    self.room_has_humpus = False
                    return True

        elif direction == 'up':
            for n in range(from_loc[0], self.gridHeight):
                room = self.grid.item((n, from_loc[1]))
                if room.has_wumpus:
                    self.wumpus_dead = True
                    self.room_has_humpus = False
                    return True

        elif direction == 'down':
            for n in reversed(range(from_loc[0], self.gridHeight)):
                room = self.grid.item((n, from_loc[1]))
                if room.has_wumpus:
                    self.wumpus_dead = True
                    self.room_has_humpus = False
                    return True

        return False

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
                if (self.grid.item(i, j).visited) or self._debug:
                    if self._is_pit((i, j)):
                        element += 'P'
                    if self._is_wumpus((i, j)):
                        element += 'W'
                    if self._is_gold((i, j)):
                        element += 'G'
                    if self._is_breeze((i, j)):
                        element += 'b'
                    if self._is_stench((i, j)):
                        element += 's'
                    if self.agent.location == (i, j):
                        if self.gold_grabbed:
                            element += 'G'
                        if self.agent.orientations[self.agent.orientation] == 'up':
                            element += u'A\u2303'
                        elif self.agent.orientations[self.agent.orientation] == 'down':
                            element += u'A\u2304'
                        elif self.agent.orientations[self.agent.orientation] == 'left':
                            element += u'A\u2039'
                        elif self.agent.orientations[self.agent.orientation] == 'right':
                            element += u'A\u203A'
                else:
                    element += ""
                row += ' ' * int(padding/2) + element + \
                    ' ' * (int(padding/2)-len(element)) + "|"
            print(row)
        print(("+" + "-" * padding) * self.gridWidth + "+")

    def set_agent(self, agent: Agent):
        self.agent = agent
        self.agent.orientation = 0
        self.agent.location = (0, 0)

    def get_percepts(self, action=None):
        percepts = {}
        if action == "f":  # forward
            newloc = self._get_next_loc(
                self.agent.location, self.agent.orientation)
            if self._will_hit_wall(newloc):
                # Redundant but just to make sure it's not changed
                self.agent.set_location(self.agent.location)
                room = self.grid.item(self.agent.location)
                percepts["stench"] = room.has_stench
                percepts["breeze"] = room.has_breeze
                percepts["glitter"] = room.has_glitter
                percepts["bump"] = True
                percepts["scream"] = self.wumpus_dead
                percepts["points"] = -1
            else:
                # New location
                self.agent.set_location(newloc)
                room = self.grid.item(newloc)
                percepts["stench"] = room.has_stench
                percepts["breeze"] = room.has_breeze
                percepts["glitter"] = room.has_glitter
                percepts["bump"] = False
                percepts["scream"] = self.wumpus_dead
                percepts["points"] = -1

                if room.has_pit:
                    percepts["points"] += -1000
                    self.agent.kill()

                if room.has_wumpus and not self.wumpus_dead:
                    percepts["points"] += -1000
                    self.agent.kill()

                room.visited = True

        elif action == "l":  # turn left
            self.agent.turn_left()
            room = self.grid.item(self.agent.location)
            percepts["stench"] = room.has_stench
            percepts["breeze"] = room.has_breeze
            percepts["glitter"] = room.has_glitter
            percepts["bump"] = False
            percepts["scream"] = self.wumpus_dead
            percepts["points"] = -1

        elif action == "r":  # turn right
            self.agent.turn_right()
            room = self.grid.item(self.agent.location)
            percepts["stench"] = room.has_stench
            percepts["breeze"] = room.has_breeze
            percepts["glitter"] = room.has_glitter
            percepts["bump"] = False
            percepts["scream"] = self.wumpus_dead
            percepts["points"] = -1

        elif action == "g":  # grab gold
            room = self.grid.item(self.agent.location)
            percepts["stench"] = room.has_stench
            percepts["breeze"] = room.has_breeze
            percepts["glitter"] = room.has_glitter
            percepts["bump"] = False
            percepts["scream"] = self.wumpus_dead
            percepts["points"] = -1

            if percepts["glitter"] and not self.gold_grabbed:
                self.gold_grabbed = True
                room.has_glitter = False

        elif action == "c":  # Climb
            room = self.grid.item(self.agent.location)
            percepts["stench"] = room.has_stench
            percepts["breeze"] = room.has_breeze
            percepts["glitter"] = room.has_glitter
            percepts["bump"] = False
            percepts["scream"] = self.wumpus_dead
            percepts["points"] = -1

            if self.agent.location == (0, 0):
                if self.allowClimbWithoutGold:
                    self.agent.exit()
                else:
                    if self.gold_grabbed:
                        percepts["points"] = 1000
                        self.agent.exit()
                    else:
                        # Not allowed to exit
                        print("Not allowed to exit without gold..")
                        pass

        elif action == "s":  # Shoot
            room = self.grid.item(self.agent.location)
            direction = self.agent.orientations[self.agent.orientation]
            self._shoot_wumpus(self.agent.location, direction)

            percepts["stench"] = room.has_stench
            percepts["breeze"] = room.has_breeze
            percepts["glitter"] = room.has_glitter
            percepts["bump"] = False
            percepts["scream"] = self.wumpus_dead
            percepts["points"] = -10

        else:
            room = self.grid.item(self.agent.location)
            percepts["stench"] = room.has_stench
            percepts["breeze"] = room.has_breeze
            percepts["glitter"] = room.has_glitter
            percepts["bump"] = False
            percepts["scream"] = self.wumpus_dead
            percepts["points"] = 0

        self.agent.increment_points(percepts["points"])

        return percepts
