import math
import numpy as np
import random
from maps import default_map
from player import RandomPlayer
from defs import *

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

    def get_state(self):
        return self.territories

    def number_of_territories(self):
        return self.territories.shape[0]
    def get_player_territories(self, player_id):
        """Returns indexes of territories the player owns"""
        return np.where(self.territories[:, 1] == player_id)[0]
    def get_player_army_count(self, player_id):
        return self.territories[ self.territories[:, 1] == player_id ][:, 0].sum()
    
    def print_update(self):
        x = [ len(self.get_player_territories(p.id)) for p in self.players ]
        print(x)

    def play(self):
        n_players = len(self.players)
        self.claim_territories()
        self.setup_armies()
        while not self.finished:
            # Every 100 turns print an update
            if (self.turn % 1000) == 0:
                self.print_update()
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
        print(f'Final turn: {self.turn}')
    def playing(self, player_id):
        """Checks whether a player is still capable of playing"""
        return player_id in self.territories[:, OWNER]
    def winner(self):
        return np.array_equal(self.territories[:, 1], np.repeat(self.territories[0, 0], self.number_of_territories()))

    def recruitment_phase(self, player_id):
        new_armies = self.get_new_armies(player_id)
        self.place_armies(player_id, new_armies)
    def place_armies(self, player_id, armies):
        player = self.players[player_id]
        changes = {}
        for _ in range(armies):
            valid_territories = self.get_player_territories(player_id)
            t = player.choose_recruitment_territory(self.get_state(), valid_territories)
            self.territories[t][ARMIES] += 1
            if t not in changes:
                changes[t] = 1
            else:
                changes[t] += 1
        for k, v in changes.items():
            #print(f'player {player_id} adds {v} armies to {self.names[k]}')
            pass
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

    def attack_phase(self, player_id):
        player = self.players[player_id]
        valid_attacks = self.get_valid_attacks(player_id)
        attack = player.choose_attack(self.get_state(), valid_attacks) 
        while attack != False:
            from_terr = attack[0]
            to_terr = attack[1]
            armies = attack[2]

            result = self.do_attack(from_terr, to_terr, armies)

            # print(f'player {player_id} attacks from {self.names[choice[0]]} to {self.names[choice[1]]} with {choice[2]} armies.')
            # print(f'The attack is {result}')

            if result == -1:
                break
            elif result == 0:
                if not player.keep_attacking(self.get_state()):
                    break
            else:
                self.reinforce_attack(player_id, from_terr, to_terr)
                attack = player.choose_attack(self.get_state(), self.get_valid_attacks(player_id, to_terr))
    def reinforce_attack(self, player_id, from_terr, to_terr):
        player = self.players[player_id]
        movable_armies = self.territories[from_terr, ARMIES] - 1
        self.territories[to_terr, ARMIES] = 1
        for _ in range(movable_armies):
            choice = player.take_action(self.get_state(), 7, (from_terr, to_terr))
            self.territories[choice, ARMIES] += 1
            
    def is_valid_attack(self, player_id, attacker_territory, defender_territory, attacker_armies):
        return 0 < attacker_armies < self.territories[attacker_armies][ARMIES] and (attacker_territory, defender_territory) in self.get_valid_attacks(player_id, attacker_territory)

    def get_valid_attacks(self, player_id, frm=-1):
        owned = self.get_player_territories(player_id)
        if frm == -1:
            valid_from = owned[np.where(self.territories[owned, ARMIES] > 1)[0]]
        else:
            valid_from = [frm] 
        if self.territories[frm, ARMIES] <= 1:
            return []
        attacks = []
        for vf_terr in valid_from:
            edges = set(self.graph[vf_terr])
            valid_to = edges - set(owned)
            for vt_terr in valid_to:
                attacks.append((vf_terr, vt_terr))
        return attacks
    def do_attack(self, attacker_territory, defender_territory, attacker_armies):
        """
        Updates state
        Returns -1 if attack fails (can't continue), 0 if attack is undecided (can continue), 1 if attack is victory
        """
        attacker_id = self.territories[attacker_territory, OWNER]
        max_attacker_armies = self.territories[attacker_territory, ARMIES]
        max_defender_armies = self.territories[defender_territory, ARMIES]
        defender_armies = min(2, max_defender_armies)

        a_rolls = []
        for _ in range(attacker_armies):
            a_rolls.append(random.randrange(1, 7))
        d_rolls = []
        for _ in range(defender_armies):
            d_rolls.append(random.randrange(1, 7))

        for _ in range(min(len(a_rolls), len(d_rolls))):
            highest_a = max(a_rolls)
            highest_d = max(d_rolls)
            a_rolls.remove(highest_a)
            d_rolls.remove(highest_d)
            if highest_a > highest_d:
                max_defender_armies -= 1
            else:
                attacker_armies -= 1
                max_attacker_armies -= 1
        if max_defender_armies == 0:
            self.territories[attacker_territory, ARMIES] = max_attacker_armies - attacker_armies
            self.territories[defender_territory, ARMIES] = attacker_armies
            self.territories[defender_territory, OWNER] = attacker_id
            result = 1
        elif max_attacker_armies == 1:
            self.territories[attacker_armies, ARMIES] = max_attacker_armies
            result = -1
        else:
            self.territories[attacker_territory, ARMIES] = max_attacker_armies
            self.territories[defender_territory, ARMIES] = max_defender_armies
            result = 0
        return result

    def fortify_phase(self, player_id):
        player = self.players[player_id]
        owned = self.get_player_territories(player_id)
        possible_moves = {}
        for t in owned:
            possible_moves[t] = self.territories[t, ARMIES] - 1
        for t in owned:
            valid_forts = self.get_valid_fortifications(t)
            for _ in range(possible_moves[t]):
                f = player.choose_fortify(self.get_state(), valid_forts)
                if f:
                    frm = f[0]
                    to = f[1]
                    self.territories[frm, ARMIES] -= 1
                    possible_moves[frm] -= 1
                    self.territories[to, ARMIES] += 1
    def get_valid_fortifications(self, territory):
        player_id = self.territories[territory][OWNER]
        edges = self.graph[territory]
        return [(territory, t) for t in edges if self.territories[t, OWNER] == player_id ]
    # Setup Stuff
    def make_state(self):
        graph_size = len(self.graph.keys())
        territory = np.array([0, -1])
        territories = np.array([territory] * graph_size)
        return territories
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