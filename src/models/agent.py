class Agent:
    location = (0, 0)
    points = 0
    orientations = ['right', 'down', 'left', 'up']
    orientation = 0

    is_dead = False
    exited = False
    has_gold = False

    def grab_gold(self):
        self.has_gold = True

    def set_location(self, location):
        self.location = location

    def turn_left(self):
        self.orientation = (
            self.orientation-1) % len(self.orientations)

    def turn_right(self):
        self.orientation = (
            self.orientation+1) % len(self.orientation)

    def exit(self):
        self.exited = True

    def is_dead(self):
        self.dead = True
