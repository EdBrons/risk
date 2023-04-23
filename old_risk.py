import math
import numpy as np
from enum import Enum, auto
from maps import default_map

ARMIES = 0
OWNER = 1

class AttackRes(Enum):
    WON = 0
    UNDECIDED = auto()
    FAILED = auto()

class Phase(Enum):
    CHOOSE_TERRITORY = 0
    RECRUITMENT = auto() 
    FIRST_ATTACK = auto()
    SUBS_ATTACK = auto()
    REINFORCE_ATTACK = auto()
    CONTINUE_ATTACK = auto()
    FORTIFY = auto()
    CONTINUE_FORTIFY = auto()


# Taken from https://github.com/civrev/RLRisk/blob/master/rlrisk/environment/risk.py
class Risk:
    def __init__(self, n_players, randomSetup = True, max_turns = math.inf):
        """
        randomSetup - should the territories be assigned randomly, and armies placed randomly
        max_turns - maximum number of turns for this game
        """
        if n_players < 2 or n_players > 6:
            raise ValueError("2 <= len(players) <= 6")
        self.n_players = n_players

        self.randomSetup = randomSetup
        self.max_turns = max_turns

        self.turn = 0
        self.current_player = 0
        self.phase = Phase.CHOOSE_TERRITORY
        self.finished = False
        
        self.armies_to_place = self.get_setup_armies() * n_players
        self.attacking = False
        self.frm = None
        self.to = None

        self.graph, self.continents, self.continent_rewards, self.names = default_map()
        self.territories = self.make_state()

    def get_territory_count(self):
        """Returns number of territories"""
        return self.territories.shape[0]
    def get_vertices_count(self):
        sum = 0
        for _, values in self.graph.items():
            sum += len(values)
        return sum
    def get_player_territories(self, player_id):
        """Returns number of territories owned by a given player"""
        return np.where(self.territories[:, 1] == player_id)[0]
    def get_player_army_count(self, player_id):
        """Returns the army count for a given player"""
        return self.territories[ self.territories[:, 1] == player_id ][:, 0].sum()
    
    def is_player_alive(self, player_id):
        """Returns True if the player has armies left, False otherwise"""
        return player_id in self.territories[:, OWNER]
    def get_next_player(self):
        """
        NOTE: possibility for an infinite loop here maybe
        in future we should do this differently
        """
        self.current_player = (self.current_player + 1) % self.n_players
        if not self.is_player_alive(self.current_player):
            self.get_next_player()
        return self.current_player
    def winner(self):
        """Returns True if there is a winner"""
        return np.array_equal(self.territories[:, OWNER], np.repeat(self.territories[0, OWNER], self.get_territory_count()))

    def get_moves(self):
        if self.phase == Phase.CHOOSE_TERRITORY:
            return (self.territories[:, OWNER] == -1 or self.territories[:, OWNER] == self.current_player).nonzero()
        if self.phase == Phase.RECRUITMENT:
            return self.get_recruitment_moves(self.current_player)
        elif self.phase == Phase.FIRST_ATTACK:
            return self.get_legal_attacks(self.current_player)
        elif self.phase == Phase.CONTINUE_ATTACK:
            return [ True, False ]
        elif self.phase == Phase.REINFORCE_ATTACK:
            return self.territories[self.frm, ARMIES] - 1
        elif self.phase == Phase.SUBS_ATTACK:
            return self.get_legal_attacks(self.current_player, self.to)
        elif self.phase == Phase.FORTIFY:
            return [ False, ( u, v ) for u in self.get_player_territories(self.current_player) for v in self.graph[u] if self.territories[u, ARMIES] > 1 and self.territories[v, OWNER] == self.current_player ]
        elif self.phase == Phase.CONTINUE_FORTIFY:
            return [ True, False ]
    def attack_res_transition(self, res):
        if res == AttackRes.WON:
            self.phase = Phase.REINFORCE_ATTACK
        elif res == AttackRes.UNDECIDED:
            self.phase = Phase.CONTINUE_ATTACK
        elif res == AttackRes.FAILED:
            self.phase = Phase.FORTIFY
            self.attacking = False
            self.frm = None
            self.to = None
    def step(self, move):
        if self.phase == Phase.CHOOSE_TERRITORY:
            if self.territories[move, OWNER] == -1 or self.territories[move, OWNER] == self.current_player:
                self.territories[move, OWNER] = self.current_player
                self.territories[move, ARMIES] += 1
                self.armies_to_place -= 1
            if self.armies_to_place <= 0:
                self.phase = Phase.RECRUITMENT
                self.current_player = 0
            else:
                self.get_next_player()
        elif self.phase == Phase.RECRUITMENT:
            if self.is_valid_recruitment(self.current_player, move):
                self.recruitment_step(move)
                self.phase = Phase.FIRST_ATTACK
        elif self.phase == Phase.FIRST_ATTACK:
            if self.is_valid_attack(self.current_player, move):
                self.attack_res_transition(self.start_attack(move))
        elif self.phase == Phase.CONTINUE_ATTACK:
            if move:
                self.attack_res_transition(self.continue_attack())
            else:
                self.phase = Phase.FORTIFY
        elif self.phase == Phase.REINFORCE_ATTACK:
            if 0 < move <= self.territories[self.frm, ARMIES] - 1:
                self.reinforce(move)
                self.phase = Phase.SUBS_ATTACK
            else:
                print('reinforce attack phase fucked up')
        elif self.phase == Phase.SUBS_ATTACK:
            if self.is_valid_subs_attack(self.current_player, move, self.to):
                self.attack_res_transition(self.start_attack(move))
        elif self.phase == Phase.FORTIFY:
            # do nothing because fuck the fortify phase
            self.current_player = self.get_next_player()
            self.phase = Phase.RECRUITMENT
    def is_valid_subs_attack(self, player_id, attack, prev):
        return prev == attack[0] and self.is_valid_attack(player_id, attack)
    def is_valid_attack(self, player_id, attack):
        frm, to = attack
        return (self.territories[frm, ARMIES] > 1
                and self.territories[frm, OWNER] == player_id
                and self.territories[to, OWNER] != player_id
                and to in self.graph[frm]
                )
    def reinforce(self, n_armies):
        self.territories[self.frm, ARMIES] -= n_armies
        self.territories[self.to, ARMIES] += n_armies
    def start_attack(self, attack):
        self.attacking = True
        self.frm, self.to = attack
        return self.do_attack(self.frm, self.to)
    def continue_attack(self):
        return self.do_attack(self.frm, self.to)
    def get_recruitment_moves(self, player_id):
        return ( self.get_new_armies(player_id), self.get_player_territories(player_id) )
    def is_valid_recruitment(self, player_id, placement):
        total_armies = sum(placement[:, ARMIES])
        return total_armies <= self.get_new_armies(player_id) and len(set(placement[:, OWNER])) == 1
    def recruitment_step(self, move):
        for m in move:
            print(f'{m[1]} armies going to {m[0]}')
            self.territories[m[OWNER], ARMIES] += m[ARMIES]

    def get_new_armies(self, player_id):
        """
        Returns the number of armies a player can recruit on their turn
        """
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

    def get_legal_attacks(self, player_id, frm=None):
        """
        Returns an array of pairs of provinces where attacks can be made: (terr_frm, terr_to)
        Will return an empty array if frm has less than 2 units
        To be legal an attack must:
        -originate from a territory owned by the player
        -That territory must have at least 2 armies
        -It must go to an adjacent territory owned by another player
        """
        owned = self.get_player_territories(player_id)
        if frm is None:
            valid_from = owned[np.where(self.territories[owned, ARMIES] > 1)[0]]
        else:
            assert self.territories[frm, OWNER] == player_id
            if self.territories[frm, ARMIES] < 2:
                return []
            valid_from = [ frm ] 
        legal_attacks = []
        for vf_terr in valid_from:
            edges = set(self.graph[vf_terr])
            valid_to = edges - set(owned)
            for vt_terr in valid_to:
                legal_attacks.append((vf_terr, vt_terr))
        return legal_attacks

    def do_attack(self, frm, to):
        # sanity checks
        assert self.territories[frm, OWNER] != self.territories[to, OWNER]
        assert self.territories[frm, ARMIES] >= 2
        assert self.territories[to, ARMIES] > 0
        assert to in self.graph[frm]

        attacker_armies = min(3, self.territories[frm, ARMIES] - 1)
        attacker_id = self.territories[frm, OWNER]
        max_attacker_armies = self.territories[frm, ARMIES]
        max_defender_armies = self.territories[to, ARMIES]
        defender_armies = min(2, max_defender_armies)

        # generate random list of rolls in descending order
        a_rolls = np.sort(np.random.randint(1, 7, attacker_armies))[::-1]
        d_rolls = np.sort(np.random.randint(1, 7, defender_armies))[::-1]
        
        print(a_rolls, d_rolls)

        for i in range(min(a_rolls.shape[0], d_rolls.shape[0])):
            if a_rolls[i] > d_rolls[i]:
                max_defender_armies -= 1
            else:
                attacker_armies -= 1
                max_attacker_armies -= 1

        if max_defender_armies == 0:
            self.territories[frm, ARMIES] = max_attacker_armies - attacker_armies
            self.territories[to, ARMIES] = attacker_armies
            self.territories[to, OWNER] = attacker_id
            result = AttackRes.WON 
        elif max_attacker_armies <= 1:
            self.territories[frm, ARMIES] = max_attacker_armies
            result = AttackRes.FAILED
        else:
            self.territories[frm, ARMIES] = max_attacker_armies
            self.territories[to, ARMIES] = max_defender_armies
            result = AttackRes.UNDECIDED

        return result

    # Setup Stuff
    def make_state(self):
        graph_size = len(self.graph.keys())
        territory = np.array([0, -1])
        territories = np.array([territory] * graph_size)
        return territories
    def random_setup(self):
        """
        Generates a random initial setup for the game, that is, the 
        territories that each player owns with their respective armies
        """
        self.claim_territories()
        self.setup_armies()
        self.phase = Phase.RECRUITMENT
    def claim_territories(self):
        order = np.resize(np.arange(self.n_players), self.get_territory_count())
        np.random.shuffle(order)
        self.territories[:, 0] = np.ones(self.get_territory_count())
        self.territories[:, 1] = order
    def get_setup_armies(self):
        players_to_initial_armies = { 2: 40, 3: 35, 4: 30, 5: 25, 6: 20 }
        return players_to_initial_armies[self.n_players]
    def setup_armies(self):
        armies_to_place_base = self.get_setup_armies()
        for p in range(self.n_players):
            armies_to_place = armies_to_place_base - len(self.get_player_territories(p))
            my_territories = np.isin(element=self.territories[:, 1], test_elements=p)
            army_placement = np.ones(my_territories.sum())
            for _ in range(armies_to_place):
                army_placement[np.random.randint(army_placement.shape[0])] += 1
            self.territories[my_territories, 0] = army_placement