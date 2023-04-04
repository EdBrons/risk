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
    def choose_recruit(self, state, valid):
        return np.random.choice(valid)
    def choose_fortify(self, state, valid):
        if valid == []:
            return False
        move = valid[random.randint(0, len(valid) - 1)]
        amount = random.randint(1, state[move[0], ARMIES] - 1)
        return move + (amount,)
    def choose_attack(self, state, valid):
        if valid == []:
            return
        if random.random() < self.peace:
            return False
        move = valid[random.randint(0, len(valid) - 1)]
        amount = random.randint(1, state[move[0], ARMIES] - 1)
        return move + (amount,)
    def keep_attacking(self, state):
        return random.random() < self.peace
    def choose_reinforce(self, state, valid):
        return np.random.choice(valid)