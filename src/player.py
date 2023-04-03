import random

class Player:
    def __init__(self, id):
        self.id = id

class RandomPlayer(Player):
    def __init__(self, id):
        super().__init__(id)