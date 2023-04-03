import math
import numpy as np
from maps import default_map
from player import RandomPlayer

NO_OWNER = -1

# Taken from https://github.com/civrev/RLRisk/blob/master/rlrisk/environment/risk.py
class Risk:
    def __init__(self, players, random_setup = True, max_turns = math.inf):
        if len(players) < 2 or len(players) > 6:
            raise ValueError("2 <= len(players) <= 6")
        self.players = players
        self.random_setup = random_setup
        self.max_turns = max_turns
        self.turn = 0
        self.finished = False
        self.graph, self.continents, self.continent_rewards, self.names = default_map()
        self.territories = self.make_state()
    def make_state(self):
        graph_size = len(self.graph.keys())
        territory = np.array([0, -1])
        territories = np.array([territory] * graph_size)
        return territories
    def number_of_territories(self):
        return self.territories.shape[0]
    def get_player_territories(self, player_id):
        """Returns indexes of territories the player owns"""
        return np.where(self.territories[:, 1] == player_id)[0]
    def get_player_army_count(self, player_id):
        return self.territories[ self.territories[:, 1] == player_id ][:, 0].sum()
    def get_new_armies(self, player_id):
        my_territories = self.get_player_territories(player_id)
        new_armies = my_territories.shape[0] // 3
        if new_armies < 3:
            new_armies = 3
        for c in self.continents:
            owned = True
            for t in self.continents[c]:
                if t not in my_territories:
                    owned = False
            if owned:
                new_armies += self.continent_rewards[c]
        return new_armies
    def claim_territories(self):
        n_players = len(self.players)
        if self.random_setup:
            order = np.resize(np.arange(n_players), self.number_of_territories())
            np.random.shuffle(order)
            self.territories[:, 0] = np.ones(self.number_of_territories())
            self.territories[:, 1] = order
        else:
            raise NotImplementedError("We haven't implemented player choice yet...")
    def setup_armies(self):
        n_players = len(self.players)
        players_to_initial_armies = { 2: 40, 3: 35, 4: 30, 5: 25, 6: 20 }
        armies_to_place_base = players_to_initial_armies[n_players]
        if self.random_setup:
            for p in self.players:
                armies_to_place = armies_to_place_base - len(self.get_player_territories(p.id))
                my_territories = np.isin(element=self.territories[:, 1], test_elements=p.id)
                army_placement = np.ones(my_territories.sum())
                for _ in range(armies_to_place):
                    army_placement[np.random.randint(army_placement.shape[0])] += 1
                self.territories[my_territories, 0] = army_placement
        else:
            raise NotImplementedError("We haven't implemented player choice yet...")
    def winner(self):
        return np.array_equal(self.territories[:, 1], np.repeat(self.territories[0, 0], self.number_of_territories()))
    def get_state(self):
        return self.territories
    def play(self):
        n_players = len(self.players)
        self.claim_territories()
        self.setup_armies()
        while not self.finished:
            player_id = self.players[self.turn % n_players].id
            self.turn += 1

            self.recruitment_phase(player_id)
            self.attack_phase(player_id)
            if self.winner():
                self.finished = True
                break
            self.fortify_phase(player_id)

            if self.turn > self.max_turns:
                self.finished = True
                break
    def recruitment_phase(self, player_id):
        new_armies = self.get_new_armies(player_id)
        self.place_armies(player_id, new_armies)
    def place_armies(self, player_id, armies):
        player = self.players[player_id]
        for _ in range(armies):
            valid = self.get_player_territories(player_id)
            t = player.take_action(self.get_state(), 0, valid)
            self.territories[t][0] += 1
    def attack_phase(self, player_id):
        pass
    def fortify_phase(self, player_id):
        pass


risk = Risk([RandomPlayer(0), RandomPlayer(1), RandomPlayer(2)], max_turns=100)
risk.play()
print(risk.get_state())