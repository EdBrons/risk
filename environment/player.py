import numpy as np
import random

class Player:
    def __init__(self, id):
        self.id = id
    def take_action(self, state, code, valid):
        return -1

class RandomPlayer(Player):
    def __init__(self, id):
        super().__init__(id)
    def choose_recruitment_territory(self, state, valid_territories):
        return np.random.choice(valid_territories)
    def choose_fortify(self, state, valid):
        if valid == []:
            return False
        return valid[random.randint(0, len(valid) - 1)]
    def choose_attack(self, state, valid_attacks):
        if len(valid_attacks) == 0:
            return False
        move = valid_attacks[random.randint(0, len(valid_attacks) - 1)]
        return move
        # amount = random.randint(1, min(state[move[0], ARMIES] - 1, 3))
        # assert amount >= 1
        # return move + (amount,)
    def keep_attacking(self, state):
        return random.random() < .5
    def choose_reinforce(self, state, valid):
        return random.random() < .5

class SmartPlayer(Player):
    def __init__(self, id):
        super().__init__(id)
    def choose_recruitment_territory(self, state, valid_territories):
        # borders = [ t for t in valid_territories if self.game.is_border(t) ]
        return np.random.choice(valid_territories)
    def choose_fortify(self, state, valid):
        if valid == []:
            return False
        return valid[random.randint(0, len(valid) - 1)]
    def choose_attack(self, state, valid_attacks):
        if len(valid_attacks) == 0:
            return False
        move = valid_attacks[random.randint(0, len(valid_attacks) - 1)]
        return move
    def keep_attacking(self, state):
        return True
    def choose_reinforce(self, state, valid):
        return True
    def test():
        pass 