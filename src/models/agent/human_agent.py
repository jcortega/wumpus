class HumanAgent:
    choices = []

    def __init__(self, choices):
        self.choices = choices

    def next_step(self, percepts=None):
        while True:
            action = input("Enter your action: ")
            if action not in self.choices:
                print("Invalid action. Try again...")
            else:
                return action
