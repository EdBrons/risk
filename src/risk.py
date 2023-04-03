import random
import numpy as np
from maps import default_map

NO_OWNER = -1

# Taken from https://github.com/civrev/RLRisk/blob/master/rlrisk/environment/risk.py
class Risk:
    def __init__(self, players, choose_territories = False):
        if len(players) < 2 or len(players) > 6:
            raise ValueError("2 <= len(players) <= 6")
        self.players = players
        self.choose_territories = choose_territories
        self.turn = 0
        self.graph, self.continents, self.continent_rewards, self.names = default_map()
        self.state = self.make_state()
    def make_state(self):
        graph_size = len(self.graph.keys())
        territory = np.array([0, -1])
        territories = np.array([territory] * graph_size)
        return territories
    def number_of_territories(self):
        return self.state.shape[0]
    def claim_territories(self):
        n_players = len(self.players)
        if self.choose_territories:
            raise NotImplementedError("")
        else:
            # randomly assigns territories to players
            order = np.resize(np.arange(n_players), self.number_of_territories())
            np.random.shuffle(order)
            self.state[:, 0] = np.ones(self.number_of_territories())
            self.state[:, 1] = order

risk = Risk(['a', 'b', 'c'])
risk.claim_territories()
print(risk.state)