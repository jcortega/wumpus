class Room:
    has_stench = False
    has_breeze = False
    has_glitter = False
    has_wumpus = False
    has_pit = False
    visited = False

    def __init__(self, has_stench=False, has_breeze=False, has_glitter=False, has_wumpus=False, has_pit=False):
        self.has_stench = has_stench
        self.has_breeze = has_breeze
        self.has_glitter = has_glitter
        self.has_wumpus = has_wumpus
        self.has_pit = has_pit

    def __str__(self):
        return str((self.has_stench, self.has_breeze, self.has_glitter, self.has_wumpus, self.has_pit))
