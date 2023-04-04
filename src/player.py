import numpy as np
import random
from defs import *

class Player:
    def __init__(self, id):
        self.id = id
    def take_action(self, state, code, valid):
        return -1

class RandomPlayer(Player):
    def __init__(self, id, peace=0.25):
        super().__init__(id)
        self.peace = peace
    def choose_recruitment_territory(self, state, valid_territories):
        return np.random.choice(valid_territories)
    def choose_fortify(self, state, valid):
        if valid == []:
            return False
            
    def choose_attack(self, state, valid_attacks):
        if len(valid_attacks) == 0:
            return False
        move = valid_attacks[random.randint(0, len(valid_attacks) - 1)]
        amount = random.randint(1, state[move[0], ARMIES] - 1)
        return move + (amount,)
    def keep_attacking(self, state):
        return random.random() < self.peace
    def choose_reinforce(self, state, valid):
        return np.random.choice(valid)