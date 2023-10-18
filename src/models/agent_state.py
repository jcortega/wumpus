class AgentState:
    location = (0, 0)
    points = 0
    orientations = ['right', 'down', 'left', 'up']
    orientation = 0
    _points = 0

    _is_dead = False
    _exited = False

    arrows = 1

    def set_location(self, location):
        self.location = location

    def turn_left(self):
        self.orientation = (
            self.orientation-1) % len(self.orientations)

    def turn_right(self):
        self.orientation = (
            self.orientation+1) % len(self.orientations)

    def exited(self):
        return self._exited

    def exit(self):
        self._exited = True

    def kill(self):
        self._is_dead = True

    def is_dead(self):
        return self._is_dead

    def increment_points(self, points):
        self._points += points

    def points(self):
        return self._points
