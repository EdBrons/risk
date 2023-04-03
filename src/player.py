import numpy as np

class Player:
    def __init__(self, id):
        self.id = id
    def take_action(self, state, code, valid):
        return -1

class RandomPlayer(Player):
    def __init__(self, id):
        super().__init__(id)
    def take_action(self, state, code, valid):
        if code == 0:
            return np.random.choice(valid)
        return super().take_action(state, code, valid)